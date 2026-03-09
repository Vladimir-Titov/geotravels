from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

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


def run_server(host: str, port: int, reload: bool) -> None:
    uvicorn.run('web.app:app', host=host, port=port, reload=reload)


def run_migrate(args: argparse.Namespace) -> None:
    settings = AppSettings()
    config = alembic_config(database_url=settings.db.database_url_for_migrations)
    command.upgrade(config, args.revision)


def run_create_revision(args: argparse.Namespace) -> None:
    settings = AppSettings()
    config = alembic_config(database_url=settings.db.database_url_for_migrations)
    command.revision(config, message=args.message, autogenerate=args.autogenerate)


def run_seed(_: argparse.Namespace) -> None:
    settings = AppSettings()
    inserted = asyncio.run(seed_countries(settings))
    print(f'Inserted {inserted} new countries')


def run_init_db(_: argparse.Namespace) -> None:
    settings = AppSettings()
    sync_url = to_sync_database_url(settings.db.database_url)
    engine = create_engine(sync_url, future=True)
    try:
        metadata.create_all(engine)
    finally:
        engine.dispose()
    print('Database schema initialized with SQLAlchemy metadata')


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='geotravels management commands')
    subparsers = parser.add_subparsers(dest='command', required=True)

    run_parser = subparsers.add_parser('run', help='Run API server')
    run_parser.add_argument('--host', default='0.0.0.0')
    run_parser.add_argument('--port', default=8000, type=int)
    run_parser.add_argument('--reload', action='store_true')

    migrate_parser = subparsers.add_parser('migrate', help='Run alembic upgrade')
    migrate_parser.add_argument('revision', nargs='?', default='head')
    migrate_parser.set_defaults(func=run_migrate)

    revision_parser = subparsers.add_parser('create-revision', help='Create alembic migration revision')
    revision_parser.add_argument('-m', '--message', required=True)
    revision_parser.add_argument('--autogenerate', action='store_true')
    revision_parser.set_defaults(func=run_create_revision)

    seed_parser = subparsers.add_parser('seed-countries', help='Load countries from GeoJSON')
    seed_parser.set_defaults(func=run_seed)

    init_parser = subparsers.add_parser('init-db', help='Create DB tables without migrations')
    init_parser.set_defaults(func=run_init_db)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == 'run':
        run_server(host=args.host, port=args.port, reload=args.reload)
        return

    args.func(args)


if __name__ == '__main__':
    main()
