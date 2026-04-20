from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import and_, func, select

from app.models.tables import cities, countries, files, files_visits, users, visits
from app.repositories.base import BaseDBRepository


class DashboardRepository(BaseDBRepository):
    async def get_user_snapshot(self, user_id: UUID) -> dict[str, Any] | None:
        query = select(
            users.c.id,
            users.c.email,
            users.c.first_name,
            users.c.last_name,
            users.c.username,
        ).where(users.c.id == user_id)
        row = await self.fetchrow(query)
        return self._normalize_user_row(row) if row else None

    async def get_stats(self, user_id: UUID) -> dict[str, int]:
        query = select(
            func.count(func.distinct(visits.c.country_code)).label('countries_count'),
            func.count(func.distinct(visits.c.city_id)).label('cities_count'),
            func.count().label('stories_count'),
        ).where(visits.c.user_id == user_id)
        row = await self.fetchrow(query)
        if not row:
            return {'countries_count': 0, 'cities_count': 0, 'stories_count': 0}

        return {
            'countries_count': int(row.get('countries_count') or 0),
            'cities_count': int(row.get('cities_count') or 0),
            'stories_count': int(row.get('stories_count') or 0),
        }

    async def list_recent_story_proxies(self, user_id: UUID, limit: int = 3) -> list[dict[str, Any]]:
        recent_visits = (
            select(
                visits.c.id,
                visits.c.country_code,
                visits.c.city_id,
                visits.c.created,
            )
            .where(visits.c.user_id == user_id)
            .order_by(visits.c.created.desc(), visits.c.id.desc())
            .limit(limit)
            .subquery()
        )

        latest_attachment = (
            select(
                files_visits.c.visit_id,
                files_visits.c.file_id,
                func.row_number()
                .over(
                    partition_by=files_visits.c.visit_id,
                    order_by=files_visits.c.id.desc(),
                )
                .label('row_num'),
            )
            .select_from(
                files_visits.join(recent_visits, recent_visits.c.id == files_visits.c.visit_id).join(
                    files,
                    files_visits.c.file_id == files.c.id,
                )
            )
            .where(
                files_visits.c.user_id == user_id,
                files_visits.c.file_id.is_not(None),
            )
            .subquery()
        )

        query = (
            select(
                recent_visits.c.id,
                recent_visits.c.country_code,
                countries.c.name.label('country_name'),
                recent_visits.c.city_id,
                cities.c.name.label('city_name'),
                recent_visits.c.created,
                latest_attachment.c.file_id.label('cover_file_id'),
            )
            .select_from(
                recent_visits.join(countries, countries.c.iso_a2 == recent_visits.c.country_code)
                .outerjoin(cities, cities.c.id == recent_visits.c.city_id)
                .outerjoin(
                    latest_attachment,
                    and_(
                        latest_attachment.c.visit_id == recent_visits.c.id,
                        latest_attachment.c.row_num == 1,
                    ),
                )
            )
            .order_by(recent_visits.c.created.desc(), recent_visits.c.id.desc())
        )

        rows = await self.fetch(query)
        return [self._normalize_recent_row(row) for row in rows]

    async def list_top_countries(self, user_id: UUID, limit: int = 3) -> list[dict[str, Any]]:
        trips_count = func.count().label('trips_count')
        query = (
            select(
                visits.c.country_code,
                countries.c.name.label('country_name'),
                trips_count,
            )
            .select_from(visits.join(countries, countries.c.iso_a2 == visits.c.country_code))
            .where(visits.c.user_id == user_id)
            .group_by(visits.c.country_code, countries.c.name)
            .order_by(trips_count.desc(), visits.c.country_code.asc())
            .limit(limit)
        )

        rows = await self.fetch(query)
        return [self._normalize_top_country_row(row) for row in rows]

    @staticmethod
    def _normalize_user_row(row: dict[str, Any]) -> dict[str, Any]:
        if isinstance(row.get('id'), str):
            row['id'] = UUID(row['id'])
        return row

    @staticmethod
    def _normalize_recent_row(row: dict[str, Any]) -> dict[str, Any]:
        if isinstance(row.get('id'), str):
            row['id'] = UUID(row['id'])
        if isinstance(row.get('city_id'), str):
            row['city_id'] = UUID(row['city_id'])
        if isinstance(row.get('cover_file_id'), str):
            row['cover_file_id'] = UUID(row['cover_file_id'])
        return row

    @staticmethod
    def _normalize_top_country_row(row: dict[str, Any]) -> dict[str, Any]:
        row['trips_count'] = int(row.get('trips_count') or 0)
        return row
