from __future__ import annotations

import asyncio
from pathlib import Path

from alembic import command
from sqlalchemy import create_engine, inspect, text

from manage import alembic_config, seed_countries
from settings import AppSettings


def test_alembic_upgrade_head_creates_tables(tmp_path: Path) -> None:
    db_path = tmp_path / 'migration_test.db'
    database_url = f'sqlite+pysqlite:///{db_path}'

    config = alembic_config(database_url=database_url)
    command.upgrade(config, 'head')

    engine = create_engine(database_url)
    inspector = inspect(engine)

    tables = set(inspector.get_table_names())
    assert {'users', 'countries', 'visits'}.issubset(tables)


def test_seed_countries_is_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / 'seed_test.db'
    database_url = f'sqlite+aiosqlite:///{db_path}'

    config = alembic_config(database_url=database_url)
    command.upgrade(config, 'head')

    settings = AppSettings(
        database_url=database_url,
        countries_geojson_path=Path('data/countries.geojson'),
    )

    inserted_first = asyncio.run(seed_countries(settings))
    inserted_second = asyncio.run(seed_countries(settings))

    assert inserted_first > 0
    assert inserted_second == 0

    sync_engine = create_engine(f'sqlite+pysqlite:///{db_path}')
    with sync_engine.begin() as conn:
        count = conn.execute(text('SELECT COUNT(*) FROM countries')).scalar_one()

    assert count == inserted_first
