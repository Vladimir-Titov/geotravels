from __future__ import annotations

from datetime import date
from typing import Any
from uuid import UUID

from app.repositories.base import PaginatedResponse
from app.repositories.visits import VisitsRepository
from app.services.exceptions import NotFoundError


class VisitsService:
    def __init__(self, visits_repository: VisitsRepository):
        self.visits_repository = visits_repository

    async def create_visit(
        self,
        user_id: UUID,
        country_code: str,
        city_id: UUID | None,
        trip_date: date | None,
    ) -> dict[str, Any]:
        return await self.visits_repository.create(
            user_id=user_id,
            country_code=country_code,
            city_id=city_id,
            trip_date=trip_date,
        )

    async def list_visits(self, user_id: UUID, limit: int, offset: int, **filters: Any) -> PaginatedResponse:
        return await self.visits_repository.paginated_search(
            order_by=['-created', '-id'],
            limit=limit,
            offset=offset,
            user_id=user_id,
            **filters,
        )

    async def get_visit_by_id(self, visit_id: UUID, user_id: UUID) -> dict[str, Any]:
        visit = await self.visits_repository.search_first_row(id=visit_id, user_id=user_id)
        if not visit:
            raise NotFoundError('Visit not found')
        return visit

    async def update_visit_by_id(self, visit_id: UUID, user_id: UUID, **payload: Any) -> dict[str, Any]:
        await self.get_visit_by_id(visit_id=visit_id, user_id=user_id)
        return await self.visits_repository.update_by_id(entity_id=visit_id, **payload)

    async def delete_visit_by_id(self, visit_id: UUID, user_id: UUID) -> None:
        await self.get_visit_by_id(visit_id=visit_id, user_id=user_id)
        await self.visits_repository.delete_by_id(entity_id=visit_id)
