from __future__ import annotations

from datetime import date
from typing import Any
from uuid import UUID

from app.repositories.countries import CountriesRepository
from app.repositories.visits import VisitsRepository
from app.services.exceptions import NotFoundError


class VisitsService:
    def __init__(
        self,
        visits_repository: VisitsRepository,
        countries_repository: CountriesRepository,
    ):
        self.visits_repository = visits_repository
        self.countries_repository = countries_repository

    async def mark_visited(
        self,
        user_id: UUID,
        country_code: str,
        trip_date: date | None,
    ) -> dict[str, Any]:
        normalized_code = country_code.upper()

        async with self.visits_repository.transaction():
            country = await self.countries_repository.get_by_code(normalized_code)
            if not country:
                raise NotFoundError('Country not found')

            return await self.visits_repository.create(
                user_id=user_id,
                country_code=normalized_code,
                trip_date=trip_date,
            )

    async def search_visits(self, user_id: UUID, **filters) -> dict[str, Any]:
        visits = await self.visits_repository.search(user_id=user_id, **filters)
        unique_codes = await self.visits_repository.list_unique_country_codes_by_user(user_id=user_id)

        return {
            'visits': visits,
            'visited_country_codes': unique_codes,
        }
