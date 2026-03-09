from __future__ import annotations

from pydantic_settings import BaseSettings

from settings.base import COMMON_MODEL_CONFIG


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


class DBSettings(BaseSettings):
    model_config = COMMON_MODEL_CONFIG

    database_url: str
    db_pool_min_size: int
    db_pool_max_size: int

    @property
    def database_url_for_migrations(self) -> str:
        return to_sync_database_url(self.database_url)

    @property
    def runtime_database_url(self) -> str:
        return to_async_database_url(self.database_url)
