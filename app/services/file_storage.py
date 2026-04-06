from __future__ import annotations

import logging
from typing import Protocol
from urllib.parse import urlparse

import aioboto3
from botocore.config import Config
from botocore.exceptions import ClientError

from settings import StorageSettings

logger = logging.getLogger(__name__)


class FileStorage(Protocol):
    async def upload_file(self, key: str, content: bytes, file_type: str | None = None) -> str: ...

    async def delete_file(self, file_url: str) -> None: ...

    async def check_connection(self) -> bool: ...


class S3FileStorage:
    def __init__(self, settings: StorageSettings):
        self._settings = settings
        self._session = aioboto3.Session()

    def _client(self):
        return self._session.client(
            's3',
            endpoint_url=self._settings.s3_endpoint_url,
            aws_access_key_id=self._settings.s3_access_key_id,
            aws_secret_access_key=self._settings.s3_secret_access_key,
            region_name=self._settings.s3_region_name,
            use_ssl=self._settings.s3_use_ssl,
            config=Config(s3={'addressing_style': 'path'}),
        )

    def _build_file_url(self, key: str) -> str:
        return f's3://{self._settings.s3_bucket_name}/{key}'

    def _extract_key(self, file_url: str) -> str:
        parsed = urlparse(file_url)
        if parsed.scheme != 's3':
            raise ValueError('Only s3:// file_url is supported')
        if parsed.netloc != self._settings.s3_bucket_name:
            raise ValueError('Unexpected bucket name in file_url')
        return parsed.path.lstrip('/')

    async def _ensure_bucket(self, client) -> None:
        try:
            await client.head_bucket(Bucket=self._settings.s3_bucket_name)
            return
        except ClientError as exc:
            error_code = str(exc.response.get('Error', {}).get('Code', ''))
            if error_code not in {'404', 'NoSuchBucket', 'NotFound'}:
                raise

        create_payload = {'Bucket': self._settings.s3_bucket_name}
        if self._settings.s3_region_name and self._settings.s3_region_name != 'us-east-1':
            create_payload['CreateBucketConfiguration'] = {'LocationConstraint': self._settings.s3_region_name}
        await client.create_bucket(**create_payload)

    async def upload_file(self, key: str, content: bytes, file_type: str | None = None) -> str:
        async with self._client() as client:
            await self._ensure_bucket(client)
            await client.put_object(
                Bucket=self._settings.s3_bucket_name,
                Key=key,
                Body=content,
                ContentType=file_type or 'application/octet-stream',
            )
        return self._build_file_url(key)

    async def delete_file(self, file_url: str) -> None:
        key = self._extract_key(file_url)
        async with self._client() as client:
            await client.delete_object(Bucket=self._settings.s3_bucket_name, Key=key)

    async def check_connection(self) -> bool:
        try:
            async with self._client() as client:
                await self._ensure_bucket(client)
            return True
        except Exception:  # noqa: BLE001
            logger.exception('S3 liveness check failed')
            return False
