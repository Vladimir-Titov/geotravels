from __future__ import annotations

from pydantic_settings import BaseSettings

from settings.base import COMMON_MODEL_CONFIG


class StorageSettings(BaseSettings):
    model_config = COMMON_MODEL_CONFIG

    s3_endpoint_url: str = 'http://localhost:9000'
    s3_access_key_id: str = 'minioadmin'
    s3_secret_access_key: str = 'minioadmin'
    s3_bucket_name: str = 'user-bucket'
    s3_region_name: str = 'us-east-1'
    s3_use_ssl: bool = False
