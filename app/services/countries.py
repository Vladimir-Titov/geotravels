from __future__ import annotations

from typing import Any

from app.repositories.base import PaginatedResponse
from app.repositories.countries import CountriesRepository


class CountriesService:
    def __init__(self, countries_repository: CountriesRepository):
        self.countries_repository = countries_repository

    async def list_countries(self, limit: int, offset: int, **filters: Any) -> PaginatedResponse:
        return await self.countries_repository.paginated_search(
            order_by='iso_a2',
            limit=limit,
            offset=offset,
            **filters,
        )
