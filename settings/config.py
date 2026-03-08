from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


def to_sync_database_url(database_url: str) -> str:
    if database_url.startswith('postgresql+asyncpg://'):
        return database_url.replace('postgresql+asyncpg://', 'postgresql+psycopg://', 1)

    if database_url.startswith('postgresql://'):
        return database_url.replace('postgresql://', 'postgresql+psycopg://', 1)

    if database_url.startswith('sqlite+aiosqlite://'):
        return database_url.replace('sqlite+aiosqlite://', 'sqlite+pysqlite://', 1)

    return database_url


def to_async_database_url(database_url: str) -> str:
    if database_url.startswith('postgresql+psycopg://'):
        return database_url.replace('postgresql+psycopg://', 'postgresql+asyncpg://', 1)

    if database_url.startswith('postgresql://'):
        return database_url.replace('postgresql://', 'postgresql+asyncpg://', 1)

    if database_url.startswith('sqlite+pysqlite://'):
        return database_url.replace('sqlite+pysqlite://', 'sqlite+aiosqlite://', 1)

    return database_url


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='GEOTRAVELS_',
        extra='ignore',
    )

    app_name: str = 'geotravels'
    environment: str = 'dev'

    database_url: str = 'postgresql+asyncpg://postgres:postgres@localhost:54441/postgres'

    jwt_secret: str = Field(default='change-me-in-prod', min_length=8)
    jwt_algorithm: str = 'HS256'
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 30

    countries_geojson_path: Path = Path('data/countries.geojson')
    db_pool_min_size: int = 5
    db_pool_max_size: int = 20

    @property
    def database_url_for_migrations(self) -> str:
        return to_sync_database_url(self.database_url)

    @property
    def runtime_database_url(self) -> str:
        return to_async_database_url(self.database_url)

    @property
    def resolved_countries_geojson_path(self) -> Path:
        if self.countries_geojson_path.is_absolute():
            return self.countries_geojson_path
        return BASE_DIR / self.countries_geojson_path


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()
