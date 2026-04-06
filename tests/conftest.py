from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from litestar.testing import TestClient
from sqlalchemy import create_engine, text

from app.models.tables import (
    achievements,
    cities,
    countries,
    followers,
    metadata,
    otp_requests,
    telegram_users,
    users,
    users_achievements,
    visits,
)
from settings import AppSettings, AuthSettings, OtpSettings, to_sync_database_url
from web.app import create_app

TEST_OTP_MOCK_CODE = '654321'


@pytest.fixture()
def settings() -> AppSettings:
    return AppSettings(
        countries_geojson_path=Path('data/countries.geojson'),
        auth=AuthSettings(jwt_secret='test-secret-123456789012345678901234', telegram_bot_token='test-token'),
        otp=OtpSettings(otp_mock_code=TEST_OTP_MOCK_CODE),
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
            conn.execute(text('CREATE SCHEMA IF NOT EXISTS tripmark'))
            conn.commit()
        metadata.create_all(sync_engine)
        with sync_engine.connect() as conn:
            # Keep reference countries, reset mutable business tables for deterministic tests.
            for table in (
                users_achievements,
                achievements,
                visits,
                followers,
                cities,
                otp_requests,
                users,
                telegram_users,
            ):
                conn.execute(table.delete())

            existing = {row[0] for row in conn.execute(text('SELECT iso_a2 FROM tripmark.countries')).fetchall()}
            to_insert = [c for c in country_rows if c['iso_a2'] not in existing]
            if to_insert:
                conn.execute(countries.insert(), to_insert)
            conn.commit()
    finally:
        sync_engine.dispose()


@pytest.fixture(autouse=True)
def mock_resend():
    with patch('resend.Emails.send', return_value={'id': 'mock-id'}):
        yield


@pytest.fixture()
def client(settings: AppSettings, db_pool):
    app = create_app(settings=settings)
    with TestClient(app=app) as test_client:
        yield test_client
