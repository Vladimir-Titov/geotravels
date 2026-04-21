from datetime import date
from typing import Any
from uuid import UUID, uuid7

from sqlalchemy import select

from app.models.tables import visits
from app.repositories.base import BaseEntityDBRepository


class VisitsRepository(BaseEntityDBRepository):
    entity = visits

    async def create(
        self,
        user_id: UUID,
        country_code: str,
        title: str,
        description: str | None,
        visibility: str,
        date_from: date,
        date_to: date | None,
        city_id: UUID | None,
        trip_date: date | None,
    ) -> dict[str, Any]:
        return await super().create(
            id=uuid7(),
            user_id=user_id,
            country_code=country_code,
            title=title,
            description=description,
            visibility=visibility,
            date_from=date_from,
            date_to=date_to,
            city_id=city_id,
            trip_date=trip_date,
        )

    async def list_by_user(self, user_id: UUID) -> list[dict[str, Any]]:
        return await self.search(user_id=user_id, order_by=['-created', '-id'])

    async def list_unique_country_codes_by_user(self, user_id: UUID) -> list[str]:
        query = (
            select(visits.c.country_code)
            .where(visits.c.user_id == user_id)
            .distinct()
            .order_by(visits.c.country_code.asc())
        )
        rows = await self.fetch(query)
        return [str(row['country_code']) for row in rows]

    def _normalize_row(self, row: dict[str, Any]) -> dict[str, Any]:
        if isinstance(row.get('id'), str):
            row['id'] = UUID(row['id'])
        if isinstance(row.get('user_id'), str):
            row['user_id'] = UUID(row['user_id'])
        if isinstance(row.get('city_id'), str):
            row['city_id'] = UUID(row['city_id'])
        return row
