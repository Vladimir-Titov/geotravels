from __future__ import annotations

from typing import Any

from app.repositories.base import PaginatedResponse
from app.repositories.cities import CitiesRepository
from app.repositories.countries import CountriesRepository
from app.services.geonames import GeoNamesClient


class ClientGeoSearchService:
    def __init__(
        self,
        countries_repository: CountriesRepository,
        cities_repository: CitiesRepository,
        geonames_client: GeoNamesClient,
    ):
        self.countries_repository = countries_repository
        self.cities_repository = cities_repository
        self.geonames_client = geonames_client

    async def search_countries(self, limit: int, offset: int, **filters: Any) -> PaginatedResponse:
        local = await self.countries_repository.paginated_search(
            order_by='iso_a2',
            limit=limit,
            offset=offset,
            **filters,
        )
        if local.pagination.total > 0:
            return local

        geonames_rows = await self.geonames_client.search_countries(filters=filters, limit=limit, offset=offset)
        await self.countries_repository.upsert_from_geonames(geonames_rows)

        return await self.countries_repository.paginated_search(
            order_by='iso_a2',
            limit=limit,
            offset=offset,
            **filters,
        )

    async def search_cities(self, limit: int, offset: int, **filters: Any) -> PaginatedResponse:
        local = await self.cities_repository.paginated_search(
            order_by='country_code,name_normalized',
            limit=limit,
            offset=offset,
            **filters,
        )
        if local.pagination.total > 0:
            return local

        geonames_rows = await self.geonames_client.search_cities(filters=filters, limit=limit, offset=offset)
        if geonames_rows:
            await self.countries_repository.upsert_from_geonames(self._countries_from_cities(geonames_rows))
            await self.cities_repository.upsert_from_geonames(geonames_rows)

        return await self.cities_repository.paginated_search(
            order_by='country_code,name_normalized',
            limit=limit,
            offset=offset,
            **filters,
        )

    def _countries_from_cities(self, city_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        countries: dict[str, dict[str, Any]] = {}
        for row in city_rows:
            country_code = str(row.get('country_code', '')).upper().strip()
            meta = row.get('meta') if isinstance(row.get('meta'), dict) else {}
            country_name = str(meta.get('countryName') or country_code).strip()
            if len(country_code) != 2 or not country_name:
                continue

            countries[country_code] = {
                'iso_a2': country_code,
                'name': country_name,
                'meta': {'countryCode': country_code, 'countryName': country_name, 'source': 'geonames-city-search'},
            }

        return list(countries.values())
