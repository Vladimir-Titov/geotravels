from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest
from litestar.testing import TestClient
from sqlalchemy import create_engine

from app.models.tables import metadata
from app.repositories.countries import CountriesRepository
from helpers import create_db_pool_from_settings
from settings import AppSettings, to_sync_database_url
from web.app import create_app


@pytest.fixture()
def settings(tmp_path: Path) -> AppSettings:
    db_path = tmp_path / 'test.db'
    return AppSettings(
        database_url=f'sqlite+aiosqlite:///{db_path}',
        jwt_secret='test-secret-123456789012345678901234',
        countries_geojson_path=Path('data/countries.geojson'),
    )


@pytest.fixture()
def db_pool(settings: AppSettings):
    sync_engine = create_engine(to_sync_database_url(settings.database_url), future=True)
    try:
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
