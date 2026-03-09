from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Protocol, runtime_checkable
from uuid import UUID

import aiosqlite
import asyncpg
from sqlalchemy.dialects.postgresql.asyncpg import dialect as postgresql_asyncpg_dialect
from sqlalchemy.dialects.sqlite import dialect as sqlite_dialect
from sqlalchemy.engine import make_url
from sqlalchemy.sql import Executable

from settings import AppSettings, DBSettings


@runtime_checkable
class DBSession(Protocol):
    async def fetch_one(self, statement: Executable) -> dict[str, Any] | None: ...

    async def fetch_all(self, statement: Executable) -> list[dict[str, Any]]: ...

    async def fetch_val(self, statement: Executable) -> Any: ...

    async def execute(self, statement: Executable) -> None: ...


@runtime_checkable
class DBPool(Protocol):
    @asynccontextmanager  # type: ignore
    async def connection(self) -> AsyncIterator[DBSession]: ...

    @asynccontextmanager  # type: ignore
    async def transaction(self) -> AsyncIterator[DBSession]: ...

    async def close(self) -> None: ...


def _compile_statement(statement: Executable, dialect: Any) -> tuple[str, list[Any]]:
    compiled = statement.compile(dialect=dialect, compile_kwargs={'render_postcompile': True})
    position_tup = getattr(compiled, 'positiontup', None)

    if position_tup:
        params = [compiled.params[key] for key in position_tup]
    else:
        params = list(compiled.params.values())

    return str(compiled), params


class AsyncpgSession:
    def __init__(self, connection: asyncpg.Connection[Any]):
        self._connection = connection
        self._dialect = postgresql_asyncpg_dialect(paramstyle='numeric_dollar')

    async def fetch_one(self, statement: Executable) -> dict[str, Any] | None:
        sql, params = _compile_statement(statement, self._dialect)
        row = await self._connection.fetchrow(sql, *params)
        return dict(row) if row else None

    async def fetch_all(self, statement: Executable) -> list[dict[str, Any]]:
        sql, params = _compile_statement(statement, self._dialect)
        rows = await self._connection.fetch(sql, *params)
        return [dict(row) for row in rows]

    async def fetch_val(self, statement: Executable) -> Any:
        sql, params = _compile_statement(statement, self._dialect)
        return await self._connection.fetchval(sql, *params)

    async def execute(self, statement: Executable) -> None:
        sql, params = _compile_statement(statement, self._dialect)
        await self._connection.execute(sql, *params)


class AsyncpgPool:
    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool

    @classmethod
    async def create(cls, settings: DBSettings) -> AsyncpgPool:
        dsn = settings.runtime_database_url
        if dsn.startswith('postgresql+asyncpg://'):
            dsn = dsn.replace('postgresql+asyncpg://', 'postgresql://', 1)

        pool = await asyncpg.create_pool(
            dsn=dsn,
            min_size=settings.db_pool_min_size,
            max_size=settings.db_pool_max_size,
        )
        return cls(pool)

    @asynccontextmanager
    async def connection(self) -> AsyncIterator[AsyncpgSession]:
        async with self._pool.acquire() as connection:
            yield AsyncpgSession(connection)

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[AsyncpgSession]:
        async with self._pool.acquire() as connection:
            async with connection.transaction():
                yield AsyncpgSession(connection)

    async def close(self) -> None:
        await self._pool.close()


class SqliteSession:
    def __init__(self, connection: aiosqlite.Connection):
        self._connection = connection
        self._dialect = sqlite_dialect(paramstyle='qmark')

    def _normalize_params(self, params: list[Any]) -> list[Any]:
        return [str(param) if isinstance(param, UUID) else param for param in params]

    async def fetch_one(self, statement: Executable) -> dict[str, Any] | None:
        sql, params = _compile_statement(statement, self._dialect)
        cursor = await self._connection.execute(sql, self._normalize_params(params))
        row = await cursor.fetchone()
        await cursor.close()
        return dict(row) if row else None

    async def fetch_all(self, statement: Executable) -> list[dict[str, Any]]:
        sql, params = _compile_statement(statement, self._dialect)
        cursor = await self._connection.execute(sql, self._normalize_params(params))
        rows = await cursor.fetchall()
        await cursor.close()
        return [dict(row) for row in rows]

    async def fetch_val(self, statement: Executable) -> Any:
        sql, params = _compile_statement(statement, self._dialect)
        cursor = await self._connection.execute(sql, self._normalize_params(params))
        row = await cursor.fetchone()
        await cursor.close()
        if not row:
            return None
        return row[0]

    async def execute(self, statement: Executable) -> None:
        sql, params = _compile_statement(statement, self._dialect)
        await self._connection.execute(sql, self._normalize_params(params))


class SqlitePool:
    def __init__(self, database_url: str):
        self._database_url = database_url

    def _database_path(self) -> str:
        url = make_url(self._database_url)
        return url.database or ':memory:'

    @asynccontextmanager
    async def connection(self) -> AsyncIterator[SqliteSession]:
        connection = await aiosqlite.connect(self._database_path())
        connection.row_factory = aiosqlite.Row
        await connection.execute('PRAGMA foreign_keys = ON')

        try:
            yield SqliteSession(connection)
        except Exception:
            await connection.rollback()
            raise
        else:
            await connection.commit()
        finally:
            await connection.close()

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[SqliteSession]:
        connection = await aiosqlite.connect(self._database_path())
        connection.row_factory = aiosqlite.Row
        await connection.execute('PRAGMA foreign_keys = ON')
        await connection.execute('BEGIN')

        try:
            yield SqliteSession(connection)
        except Exception:
            await connection.rollback()
            raise
        else:
            await connection.commit()
        finally:
            await connection.close()

    async def close(self) -> None:
        return None


async def create_db_pool_from_settings(settings: AppSettings) -> DBPool:
    db_settings = settings.db
    runtime_url = db_settings.runtime_database_url

    if runtime_url.startswith('postgresql+asyncpg://'):
        return await AsyncpgPool.create(db_settings)

    if runtime_url.startswith('sqlite+aiosqlite://'):
        return SqlitePool(runtime_url)

    raise ValueError(f'Unsupported runtime database URL: {runtime_url}')
