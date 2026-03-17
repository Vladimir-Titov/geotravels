from __future__ import annotations

import json

import pytest_asyncio
from sqlalchemy import create_engine, text

from app.models.tables import countries_table, metadata
from helpers import create_db_pool_from_settings
from settings import to_sync_database_url


@pytest_asyncio.fixture()
async def db_pool(settings):
    geojson_path = settings.resolved_countries_geojson_path
    with geojson_path.open('r', encoding='utf-8') as source:
        payload = json.load(source)

    countries = []
    for feature in payload.get('features', []):
        props = feature.get('properties', {})
        countries.append({'iso_a2': props['iso_a2'], 'name': props['name']})

    sync_engine = create_engine(to_sync_database_url(settings.db.database_url), future=True)
    try:
        with sync_engine.connect() as conn:
            conn.execute(text('CREATE SCHEMA IF NOT EXISTS tripmark'))
            conn.commit()
        metadata.create_all(sync_engine)
        with sync_engine.connect() as conn:
            existing = {row[0] for row in conn.execute(text('SELECT iso_a2 FROM tripmark.countries')).fetchall()}
            to_insert = [c for c in countries if c['iso_a2'] not in existing]
            if to_insert:
                conn.execute(countries_table.insert(), to_insert)
            conn.commit()
    finally:
        sync_engine.dispose()

    pool = await create_db_pool_from_settings(settings)
    yield pool
    await pool.close()
