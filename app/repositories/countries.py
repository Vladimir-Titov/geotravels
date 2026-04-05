from typing import Any

from app.models.tables import countries
from app.repositories.base import BaseEntityDBRepository


class CountriesRepository(BaseEntityDBRepository):
    entity = countries

    async def list_all(self, **filters) -> list[dict[str, Any]]:
        return await self.search(**filters)

    async def get_by_code(self, country_code: str) -> dict[str, Any] | None:
        return await self.search_first_row(iso_a2=country_code)

    async def insert_missing(self, countries: list[dict[str, str]]) -> int:
        if not countries:
            return 0

        async with self.transaction():
            existing_rows = await self.search(order_by='iso_a2')
            existing_codes = {row['iso_a2'] for row in existing_rows}
            to_insert = [item for item in countries if item['iso_a2'] not in existing_codes]
            await self.create_many(to_insert)  # pyright: ignore[reportArgumentType]
            return len(to_insert)
