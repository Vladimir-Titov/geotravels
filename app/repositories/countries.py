import json
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.sql import ColumnElement

from app.models import countries
from app.repositories.base import BaseEntityDBRepository, PaginatedResponse, Pagination


class CountriesRepository(BaseEntityDBRepository):
    entity = countries

    def _normalize_row(self, row: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(row)
        for field_name in ('labels', 'meta'):
            value = normalized.get(field_name)
            if isinstance(value, str):
                try:
                    normalized[field_name] = json.loads(value)
                except json.JSONDecodeError:
                    normalized[field_name] = value
        return normalized

    async def list_all(self, **filters) -> list[dict[str, Any]]:
        return await self.search(**filters)

    async def get_by_code(self, country_code: str) -> dict[str, Any] | None:
        return await self.search_first_row(iso_a2=country_code)

    async def paginated_search_by_name_or_label(
        self,
        *,
        lang: str,
        name_filter_name: str,
        name_filter_value: str,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int = 0,
        **filters: Any,
    ) -> PaginatedResponse:
        items_query = self._build_name_or_label_query(
            lang=lang,
            name_filter_name=name_filter_name,
            name_filter_value=name_filter_value,
            order_by=order_by,
            limit=limit,
            offset=offset,
            **filters,
        )
        count_base_query = self._build_name_or_label_query(
            lang=lang,
            name_filter_name=name_filter_name,
            name_filter_value=name_filter_value,
            **filters,
        )
        count_query = select(func.count()).select_from(count_base_query.subquery())

        items = self._normalize_rows(await self.fetch(items_query))
        total = int(await self.fetchval(count_query) or 0)
        return PaginatedResponse(items=items, pagination=Pagination(limit=limit, offset=offset, total=total))

    def _build_name_or_label_query(
        self,
        *,
        lang: str,
        name_filter_name: str,
        name_filter_value: str,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int = 0,
        **filters: Any,
    ) -> Any:
        query = select(self.entity)
        query = self._apply_filters(query, **filters)
        query = query.where(
            or_(
                self._get_filter_bool_expression(name_filter_name, name_filter_value),
                self._get_label_filter_expression(lang, name_filter_name, name_filter_value),
            )
        )

        for item in self._resolve_order_by(order_by):
            query = query.order_by(item)

        if limit is not None:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        return query

    def _get_label_filter_expression(
        self,
        lang: str,
        name_filter_name: str,
        name_filter_value: str,
    ) -> ColumnElement[bool]:
        label = self.entity.c.labels[lang].astext
        if name_filter_name == 'name':
            return label == name_filter_value
        if name_filter_name == 'name_like':
            return label.like(name_filter_value)
        if name_filter_name == 'name_ilike':
            return label.ilike(name_filter_value)

        raise ValueError(f'Unsupported label filter ({name_filter_name})')

    async def insert_missing(self, countries: list[dict[str, str]]) -> int:
        if not countries:
            return 0

        async with self.transaction():
            existing_rows = await self.search(order_by='iso_a2')
            existing_codes = {row['iso_a2'] for row in existing_rows}
            to_insert = [item for item in countries if item['iso_a2'] not in existing_codes]
            await self.create_many(to_insert)  # pyright: ignore[reportArgumentType]
            return len(to_insert)
