from collections.abc import Sequence
from typing import Any
from uuid import UUID, uuid7

from sqlalchemy import select

from app.models.tables import cities, visits_cities
from app.repositories.base import BaseDBRepository


class VisitsCitiesRepository(BaseDBRepository):
    @staticmethod
    def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
        if isinstance(row.get('id'), str):
            row['id'] = UUID(row['id'])
        if isinstance(row.get('visit_id'), str):
            row['visit_id'] = UUID(row['visit_id'])
        if isinstance(row.get('city_id'), str):
            row['city_id'] = UUID(row['city_id'])
        return row

    @staticmethod
    def _deduplicate_city_ids(city_ids: Sequence[UUID]) -> list[UUID]:
        # Preserve order from request while dropping duplicates.
        return list(dict.fromkeys(city_ids))

    async def replace_cities_for_visit(self, visit_id: UUID, city_ids: Sequence[UUID]) -> None:
        unique_city_ids = self._deduplicate_city_ids(city_ids)

        await self.fetchval(visits_cities.delete().where(visits_cities.c.visit_id == visit_id))
        if not unique_city_ids:
            return

        payload = [
            {
                'id': uuid7(),
                'visit_id': visit_id,
                'city_id': city_id,
            }
            for city_id in unique_city_ids
        ]
        query = visits_cities.insert().values(payload).returning(visits_cities.c.id)
        await self.fetch(query)

    async def list_city_ids_for_visits(self, visit_ids: Sequence[UUID]) -> dict[UUID, list[UUID]]:
        if not visit_ids:
            return {}

        query = (
            select(visits_cities.c.visit_id, visits_cities.c.city_id)
            .where(visits_cities.c.visit_id.in_(visit_ids))
            .order_by(visits_cities.c.visit_id.asc(), visits_cities.c.id.asc())
        )
        rows = await self.fetch(query)

        by_visit: dict[UUID, list[UUID]] = {visit_id: [] for visit_id in visit_ids}
        for raw_row in rows:
            row = self._normalize_row(raw_row)
            visit_id = row['visit_id']
            city_id = row['city_id']
            by_visit.setdefault(visit_id, []).append(city_id)
        return by_visit

    async def list_cities_for_visits(self, visit_ids: Sequence[UUID]) -> dict[UUID, list[dict[str, Any]]]:
        if not visit_ids:
            return {}

        query = (
            select(visits_cities.c.visit_id, cities.c.id, cities.c.name, cities.c.country_code)
            .select_from(visits_cities.join(cities, cities.c.id == visits_cities.c.city_id))
            .where(visits_cities.c.visit_id.in_(visit_ids))
            .order_by(visits_cities.c.visit_id.asc(), visits_cities.c.created.asc(), visits_cities.c.id.asc())
        )
        rows = await self.fetch(query)

        by_visit: dict[UUID, list[dict[str, Any]]] = {visit_id: [] for visit_id in visit_ids}
        for raw_row in rows:
            row = self._normalize_row(raw_row)
            visit_id = row['visit_id']
            by_visit.setdefault(visit_id, []).append(
                {
                    'id': row['id'],
                    'name': row['name'],
                    'country_code': row['country_code'],
                }
            )
        return by_visit
