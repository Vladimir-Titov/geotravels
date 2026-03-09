# pyright: reportCallIssue=false
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

import click
import uvicorn
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine

from app.models.tables import metadata
from app.repositories.countries import CountriesRepository
from helpers import create_db_pool_from_settings
from settings import AppSettings, to_sync_database_url

BASE_DIR = Path(__file__).resolve().parent


def alembic_config(database_url: str | None = None) -> Config:
    config = Config(str(BASE_DIR / 'alembic.ini'))
    config.set_main_option('script_location', str(BASE_DIR / 'migrations'))
    if database_url:
        config.set_main_option('sqlalchemy.url', to_sync_database_url(database_url))
    return config


async def seed_countries(settings: AppSettings) -> int:
    geojson_path = settings.resolved_countries_geojson_path
    with geojson_path.open('r', encoding='utf-8') as source:
        payload = json.load(source)

    countries = []
    for feature in payload.get('features', []):
        props = feature.get('properties', {})
        iso = str(props.get('iso_a2', '')).upper()
        name = str(props.get('name', '')).strip()
        if len(iso) != 2 or not name:
            continue
        countries.append({'iso_a2': iso, 'name': name})

    db_pool = await create_db_pool_from_settings(settings)
    repository = CountriesRepository(db_pool)
    try:
        return await repository.insert_missing(countries)
    finally:
        await db_pool.close()


def run_server(reload: bool) -> None:
    host = os.getenv('UVICORN_HOST', '0.0.0.0')
    port = int(os.getenv('UVICORN_PORT', '8000'))
    uvicorn.run('web.app:app', host=host, port=port, reload=reload)


def run_migrate(revision: str) -> None:
    settings = AppSettings()
    config = alembic_config(database_url=settings.db.database_url_for_migrations)
    command.upgrade(config, revision)


def run_create_revision(message: str, autogenerate: bool) -> None:
    settings = AppSettings()
    config = alembic_config(database_url=settings.db.database_url_for_migrations)
    command.revision(config, message=message, autogenerate=autogenerate)


def run_seed() -> None:
    settings = AppSettings()
    inserted = asyncio.run(seed_countries(settings))
    print(f'Inserted {inserted} new countries')


def run_init_db() -> None:
    settings = AppSettings()
    sync_url = to_sync_database_url(settings.db.database_url)
    engine = create_engine(sync_url, future=True)
    try:
        metadata.create_all(engine)
    finally:
        engine.dispose()
    print('Database schema initialized with SQLAlchemy metadata')


@click.group(help='geotravels management commands')
def cli() -> None:
    pass


@cli.command(help='Run API server')
@click.option('--reload', is_flag=True, default=False)
def run(reload: bool) -> None:
    run_server(reload=reload)


@cli.command(help='Run alembic upgrade')
@click.argument('revision', required=False, default='head')
def migrate(revision: str) -> None:
    run_migrate(revision=revision)


@cli.command(name='create-revision', help='Create alembic migration revision')
@click.option('-m', '--message', required=True)
@click.option('--autogenerate', is_flag=True, default=False)
def create_revision(message: str, autogenerate: bool) -> None:
    run_create_revision(message=message, autogenerate=autogenerate)


@cli.command(name='seed-countries', help='Load countries from GeoJSON')
def seed_countries_command() -> None:
    run_seed()


@cli.command(name='init-db', help='Create DB tables without migrations')
def init_db_command() -> None:
    run_init_db()


def main() -> None:
    cli()


if __name__ == '__main__':
    main()
