from __future__ import annotations

from collections.abc import AsyncIterator, Mapping, Sequence
from contextlib import asynccontextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import Select, Table, column, func, select
from sqlalchemy.sql import ColumnElement

from helpers import DBPool, DBSession

db_ctx: ContextVar[DBSession | DBPool | None] = ContextVar('db_ctx', default=None)


class RowNotFoundError(RuntimeError):
    pass


@dataclass(slots=True)
class Pagination:
    limit: int | None
    offset: int
    total: int


@dataclass(slots=True)
class PaginatedResponse:
    items: list[dict[str, Any]]
    pagination: Pagination


class BaseDBRepository:
    def __init__(self, db_pool: DBPool):
        self._db_pool = db_pool

    @asynccontextmanager
    async def connection(self) -> AsyncIterator[DBSession]:
        current = db_ctx.get()
        if isinstance(current, DBSession):
            yield current
            return

        pool = current if isinstance(current, DBPool) else self._db_pool
        async with pool.connection() as conn:
            token = db_ctx.set(conn)
            try:
                yield conn
            finally:
                db_ctx.reset(token)

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[DBSession]:
        current = db_ctx.get()
        if isinstance(current, DBSession):
            yield current
            return

        pool = current if isinstance(current, DBPool) else self._db_pool
        async with pool.transaction() as conn:
            token = db_ctx.set(conn)
            try:
                yield conn
            finally:
                db_ctx.reset(token)

    async def fetch(self, query: Any) -> list[dict[str, Any]]:
        async with self.connection() as conn:
            return await conn.fetch_all(query)

    async def fetchrow(self, query: Any) -> dict[str, Any] | None:
        async with self.connection() as conn:
            return await conn.fetch_one(query)

    async def fetchval(self, query: Any) -> Any:
        async with self.connection() as conn:
            return await conn.fetch_val(query)


class BaseEntityDBRepository(BaseDBRepository):
    entity: Table
    entity_versions: Table | None = None
    base_search_query: Select[Any] | None = None

    @property
    def has_version(self) -> bool:
        return self.entity_versions is not None

    def _normalize_row(self, row: dict[str, Any]) -> dict[str, Any]:
        return row

    def _normalize_rows(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [self._normalize_row(row) for row in rows]

    def _resolve_column(self, name: str, base_query: Select[Any] | None = None) -> ColumnElement[Any]:
        if base_query is not None:
            keys = set(base_query.selected_columns.keys())
            if name in keys:
                return base_query.selected_columns[name]
            return column(name)

        if name in self.entity.columns:
            return self.entity.columns[name]

        raise ValueError(f'Unknown filter column ({name})')

    def _get_filter_bool_expression(
        self,
        filter_name: str,
        filter_value: Any,
        base_query: Select[Any] | None = None,
    ) -> ColumnElement[bool]:
        if base_query is not None and filter_name in set(base_query.selected_columns.keys()):
            return self._resolve_column(filter_name, base_query=base_query) == filter_value

        if base_query is None and filter_name in self.entity.columns:
            return self.entity.columns[filter_name] == filter_value

        split_by_underscore = filter_name.split('_')
        sign = split_by_underscore.pop()
        col_name = '_'.join(split_by_underscore)
        col = self._resolve_column(col_name, base_query=base_query)

        if sign in {'lt', 'le', 'gt', 'ge', 'ne'}:
            return getattr(col, f'__{sign}__')(filter_value)
        if sign == 'in':
            return col.in_(filter_value)
        if sign == 'notin':
            return ~col.in_(filter_value)
        if sign == 'is':
            return col.is_(filter_value)
        if sign == 'isnot':
            return col.is_not(filter_value)
        if sign == 'like':
            return col.like(filter_value)
        if sign == 'ilike':
            return col.ilike(filter_value)

        raise ValueError(f'Unknown filter name ({filter_name})')

    def _apply_filters(
        self,
        query: Any,
        base_query: Select[Any] | None = None,
        **filters: Any,
    ) -> Any:
        for filter_name, filter_value in filters.items():
            query = query.where(self._get_filter_bool_expression(filter_name, filter_value, base_query=base_query))

        return query

    def _resolve_order_by(self, order_by: Sequence[Any] | str | None) -> list[Any]:
        if order_by is None:
            return []

        items: list[Any]
        if isinstance(order_by, str):
            items = [item.strip() for item in order_by.split(',') if item.strip()]
        else:
            items = list(order_by)

        resolved: list[Any] = []
        for item in items:
            if isinstance(item, str):
                desc = item.startswith('-')
                field_name = item[1:] if desc else item
                col = self._resolve_column(field_name, base_query=self.base_search_query)
                resolved.append(col.desc() if desc else col.asc())
            else:
                resolved.append(item)

        return resolved

    def _build_search_query(
        self,
        order_by: Sequence[Any] | str | None = None,
        limit: int | None = None,
        offset: int = 0,
        **filters: Any,
    ) -> Any:
        query = self.base_search_query if self.base_search_query is not None else select(self.entity)
        query = self._apply_filters(query, base_query=self.base_search_query, **filters)

        for item in self._resolve_order_by(order_by):
            query = query.order_by(item)

        if limit is not None:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        return query

    async def count(self, **filters: Any) -> int:
        base_query = self.base_search_query if self.base_search_query is not None else select(self.entity)
        filtered = self._apply_filters(base_query, base_query=self.base_search_query, **filters)
        count_query = select(func.count()).select_from(filtered.subquery())
        value = await self.fetchval(count_query)
        return int(value or 0)

    async def create(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        if args and kwargs:
            raise ValueError('Use either args or kwargs')

        if args:
            if len(args) != 1 or not isinstance(args[0], Mapping):
                raise ValueError('Expected single mapping positional argument')
            payload = dict(args[0])
        else:
            payload = kwargs

        query = self.entity.insert().values(**payload).returning(self.entity)
        row = await self.fetchrow(query)
        if not row:
            raise RuntimeError('No row has been created')
        return self._normalize_row(row)

    async def create_many(self, payload: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
        if not payload:
            return []
        query = self.entity.insert().values([dict(item) for item in payload]).returning(self.entity)
        rows = await self.fetch(query)
        return self._normalize_rows(rows)

    async def search(
        self,
        order_by: Sequence[Any] | str | None = None,
        limit: int | None = None,
        offset: int = 0,
        **filters: Any,
    ) -> list[dict[str, Any]]:
        query = self._build_search_query(order_by=order_by, limit=limit, offset=offset, **filters)
        rows = await self.fetch(query)
        return self._normalize_rows(rows)

    async def search_for_update(
        self,
        order_by: Sequence[Any] | str | None = None,
        limit: int | None = None,
        offset: int = 0,
        skip_locked: bool = False,
        **filters: Any,
    ) -> list[dict[str, Any]]:
        query = self._build_search_query(order_by=order_by, limit=limit, offset=offset, **filters)
        query = query.with_for_update(skip_locked=skip_locked)
        rows = await self.fetch(query)
        return self._normalize_rows(rows)

    async def get_by_id(self, entity_id: int | UUID) -> dict[str, Any]:
        row = await self.fetchrow(select(self.entity).where(self.entity.columns['id'] == entity_id))
        if not row:
            raise RowNotFoundError()
        return self._normalize_row(row)

    async def get_or_create(self, **kwargs: Any) -> dict[str, Any]:
        existing_rows = await self.search(**kwargs)
        if len(existing_rows) == 1:
            return existing_rows[0]
        if len(existing_rows) > 1:
            raise ValueError(f'Ambiguous value for {kwargs}')

        return await self.create(**kwargs)

    async def update_by_id(self, entity_id: int | UUID, **payload: Any) -> dict[str, Any]:
        query = (
            self.entity.update().where(self.entity.columns['id'] == entity_id).values(**payload).returning(self.entity)
        )
        row = await self.fetchrow(query)
        if not row:
            raise RowNotFoundError('No row has been updated')
        return self._normalize_row(row)

    async def update(self, payload: Mapping[str, Any], **filters: Any) -> list[dict[str, Any]]:
        query = self.entity.update().values(**dict(payload)).returning(self.entity)
        query = self._apply_filters(query, **filters)
        rows = await self.fetch(query)
        return self._normalize_rows(rows)

    async def archive_by_id(self, entity_id: int | UUID, **additional_payload: Any) -> dict[str, Any]:
        payload = {'archived': True, **additional_payload}
        return await self.update_by_id(entity_id=entity_id, **payload)

    async def archive(
        self,
        additional_payload: dict[str, Any] | None = None,
        **filters: Any,
    ) -> list[dict[str, Any]]:
        payload = {'archived': True, **(additional_payload or {})}
        return await self.update(payload, **filters)

    async def search_first_row(
        self,
        order_by: Sequence[Any] | str | None = None,
        offset: int = 0,
        **filters: Any,
    ) -> dict[str, Any] | None:
        results = await self.search(order_by=order_by, limit=1, offset=offset, **filters)
        return results[0] if results else None

    async def paginated_search(
        self,
        order_by: Sequence[Any] | str | None = None,
        limit: int | None = None,
        offset: int = 0,
        **filters: Any,
    ) -> PaginatedResponse:
        items = await self.search(order_by, limit, offset, **filters)
        total = await self.count(**filters)
        return PaginatedResponse(items=items, pagination=Pagination(limit=limit, offset=offset, total=total))

    async def delete_by_id(self, entity_id: int | UUID) -> dict[str, Any]:
        query = self.entity.delete().where(self.entity.columns['id'] == entity_id)
        return await self.fetchval(query)
