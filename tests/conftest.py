from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest
from litestar.testing import TestClient
from sqlalchemy import create_engine, text

from app.models.tables import metadata
from app.repositories.countries import CountriesRepository
from helpers import create_db_pool_from_settings
from settings import AppSettings, AuthSettings, DBSettings, to_sync_database_url
from web.app import create_app


@pytest.fixture()
def settings() -> AppSettings:
    return AppSettings(
        countries_geojson_path=Path('data/countries.geojson'),
        auth=AuthSettings(jwt_secret='test-secret-123456789012345678901234', telegram_bot_token='test-token'),
    )


@pytest.fixture()
def db_pool(settings: AppSettings):
    sync_engine = create_engine(to_sync_database_url(settings.db.database_url), future=True)
    try:
        with sync_engine.connect() as conn:
            conn.execute(text('CREATE SCHEMA IF NOT EXISTS tripmark'))
            conn.commit()
        metadata.create_all(sync_engine)
    finally:
        sync_engine.dispose()

    geojson_path = settings.resolved_countries_geojson_path
    with geojson_path.open('r', encoding='utf-8') as source:
        payload = json.load(source)

    countries = []
    for feature in payload.get('features', []):
        props = feature.get('properties', {})
        countries.append({'iso_a2': props['iso_a2'], 'name': props['name']})

    async def _prepare():
        pool = await create_db_pool_from_settings(settings)
        repo = CountriesRepository(pool)
        await repo.insert_missing(countries)
        return pool

    pool = asyncio.run(_prepare())

    yield pool

    asyncio.run(pool.close())


@pytest.fixture()
def client(settings: AppSettings, db_pool):
    app = create_app(settings=settings, db_pool=db_pool)
    with TestClient(app=app) as test_client:
        yield test_client
