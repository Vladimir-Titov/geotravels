import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from litestar.testing import TestClient
from sqlalchemy import create_engine, text

os.environ['GEOTRAVELS_ENVIRONMENT'] = 'test'
os.environ['GEOTRAVELS_SENTRY_ENABLE'] = 'false'

from app.models import countries, metadata
from settings import AppSettings, AuthSettings, ClientGeoSettings, LogSettings, OtpSettings, to_sync_database_url
from web.app import create_app

TEST_OTP_MOCK_CODE = '654321'


class TestFileStorage:
    def __init__(self) -> None:
        self._objects: dict[str, bytes] = {}

    def build_file_url(self, key: str) -> str:
        return f'memory://{key}'

    async def upload_file(self, key: str, content: bytes, file_type: str | None = None) -> str:  # noqa: ARG002
        self._objects[key] = content
        return self.build_file_url(key)

    async def exists_file(self, file_url: str) -> bool:
        key = file_url.removeprefix('memory://')
        return key in self._objects

    async def delete_file(self, file_url: str) -> None:
        key = file_url.removeprefix('memory://')
        self._objects.pop(key, None)

    async def download_file(self, file_url: str) -> bytes:
        key = file_url.removeprefix('memory://')
        return self._objects[key]

    async def check_connection(self) -> bool:
        return True


@pytest.fixture()
def settings() -> AppSettings:
    return AppSettings(
        environment='test',
        countries_geojson_path=Path('data/countries.geojson'),
        auth=AuthSettings(
            jwt_secret='test-secret-123456789012345678901234',
            telegram_bot_token='test-token',
            yandex_client_id='test-yandex-client',
            yandex_client_secret='test-yandex-secret',
        ),
        otp=OtpSettings(otp_mock_code=TEST_OTP_MOCK_CODE),
        client_geo=ClientGeoSettings(
            geonames_username='demo',
        ),
        log=LogSettings(sentry_enable=False),
    )


@pytest.fixture()
def db_pool(settings: AppSettings):
    geojson_path = settings.resolved_countries_geojson_path
    with geojson_path.open('r', encoding='utf-8') as source:
        payload = json.load(source)

    country_rows = []
    for feature in payload.get('features', []):
        props = feature.get('properties', {})
        country_rows.append({'iso_a2': props['iso_a2'], 'name': props['name']})

    sync_engine = create_engine(to_sync_database_url(settings.db.database_url), future=True)
    try:
        with sync_engine.connect() as conn:
            conn.execute(text('DROP SCHEMA IF EXISTS tripmark CASCADE'))
            conn.execute(text('CREATE SCHEMA tripmark'))
            conn.commit()
        metadata.create_all(sync_engine)
        with sync_engine.connect() as conn:
            conn.execute(countries.insert(), country_rows)
            conn.commit()
    finally:
        sync_engine.dispose()


@pytest.fixture(autouse=True)
def mock_resend():
    with patch('resend.Emails.send', return_value={'id': 'mock-id'}):
        yield


@pytest.fixture()
def client(settings: AppSettings, db_pool):
    app = create_app(settings=settings, file_storage=TestFileStorage())
    with TestClient(app=app) as test_client:
        yield test_client
