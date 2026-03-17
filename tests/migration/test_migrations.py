from __future__ import annotations

import asyncio
from pathlib import Path

from alembic import command
from sqlalchemy import create_engine, inspect, text

from app.models.tables import metadata
from manage import alembic_config, seed_countries
from settings import AppSettings, to_sync_database_url


def _sync_url() -> str:
    return to_sync_database_url(AppSettings().db.database_url)


def test_alembic_upgrade_head_creates_tables() -> None:
    database_url = _sync_url()
    engine = create_engine(database_url)
    try:
        with engine.connect() as conn:
            conn.execute(text('DROP SCHEMA IF EXISTS tripmark CASCADE'))
            conn.execute(text('DROP TABLE IF EXISTS alembic_version'))
            conn.commit()

        config = alembic_config(database_url=database_url)
        command.upgrade(config, 'head')

        inspector = inspect(engine)
        tables = set(inspector.get_table_names(schema='tripmark'))
        assert {'users', 'countries', 'visits', 'telegram_users'}.issubset(tables)
    finally:
        with engine.connect() as conn:
            conn.execute(text('DROP SCHEMA IF EXISTS tripmark CASCADE'))
            conn.execute(text('DROP TABLE IF EXISTS alembic_version'))
            conn.commit()
        engine.dispose()


def test_seed_countries_is_idempotent() -> None:
    settings = AppSettings(countries_geojson_path=Path('data/countries.geojson'))
    database_url = _sync_url()
    engine = create_engine(database_url)
    try:
        with engine.connect() as conn:
            conn.execute(text('DROP SCHEMA IF EXISTS tripmark CASCADE'))
            conn.execute(text('CREATE SCHEMA tripmark'))
            conn.commit()
        metadata.create_all(engine)

        inserted_first = asyncio.run(seed_countries(settings))
        inserted_second = asyncio.run(seed_countries(settings))

        assert inserted_first > 0
        assert inserted_second == 0

        with engine.connect() as conn:
            count = conn.execute(text('SELECT COUNT(*) FROM tripmark.countries')).scalar_one()
        assert count == inserted_first
    finally:
        with engine.connect() as conn:
            conn.execute(text('DROP SCHEMA IF EXISTS tripmark CASCADE'))
            conn.commit()
        engine.dispose()
