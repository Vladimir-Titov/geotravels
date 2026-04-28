import json
from typing import Any
from uuid import UUID

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

        geonames_rows = await self.geonames_client.search_countries(
            query=self._extract_query(filters, keys=('name', 'name_ilike', 'name_like')),
            country_codes=self._extract_country_codes(filters, keys=('iso_a2', 'iso_a2_in')),
            limit=limit,
            offset=offset,
        )
        await self._upsert_countries(geonames_rows)

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

        geonames_rows = await self.geonames_client.search_cities(
            query=self._extract_query(
                filters,
                keys=(
                    'name',
                    'name_ilike',
                    'name_like',
                    'name_normalized',
                    'name_normalized_ilike',
                    'name_normalized_like',
                ),
            ),
            country_code=self._extract_country_code(filters),
            limit=limit,
            offset=offset,
        )
        if geonames_rows:
            await self._upsert_countries(self._countries_from_cities(geonames_rows))
            await self._upsert_cities(geonames_rows)

        return await self.cities_repository.paginated_search(
            order_by='country_code,name_normalized,-population',
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

    async def _upsert_countries(self, payload: list[dict[str, Any]]) -> int:
        if not payload:
            return 0

        deduplicated: dict[str, dict[str, Any]] = {}
        for item in payload:
            iso_a2 = str(item.get('iso_a2', '')).upper().strip()
            name = str(item.get('name', '')).strip()
            if len(iso_a2) != 2 or not name:
                continue
            deduplicated[iso_a2] = {
                'name': name,
                'meta': item.get('meta'),
                'labels': item.get('labels'),
            }

        if not deduplicated:
            return 0

        country_codes = list(deduplicated.keys())

        async with self.countries_repository.transaction():
            existing_rows = await self.countries_repository.search(iso_a2_in=country_codes)
            existing_codes = {row['iso_a2'] for row in existing_rows}
            to_insert = [
                {
                    'iso_a2': iso_a2,
                    'name': country_payload['name'],
                    'meta': self._serialize_json_field(country_payload.get('meta')),
                    'labels': self._serialize_json_field(country_payload.get('labels')),
                }
                for iso_a2, country_payload in deduplicated.items()
                if iso_a2 not in existing_codes
            ]
            if not to_insert:
                return 0

            await self.countries_repository.create_many(to_insert)
            return len(to_insert)

    async def _upsert_cities(self, payload: list[dict[str, Any]]) -> int:
        if not payload:
            return 0

        deduplicated: dict[UUID, dict[str, Any]] = {}
        for item in payload:
            city_id = item.get('id')
            if not isinstance(city_id, UUID):
                continue
            country_code = str(item.get('country_code', '')).upper().strip()
            name = str(item.get('name', '')).strip()
            name_normalized = str(item.get('name_normalized', '')).strip()
            if len(country_code) != 2 or not name or not name_normalized:
                continue
            deduplicated[city_id] = {
                'country_code': country_code,
                'name': name,
                'name_normalized': name_normalized,
                'latitude': item.get('latitude'),
                'longitude': item.get('longitude'),
                'population': item.get('population'),
                'labels': item.get('labels'),
                'meta': item.get('meta'),
            }

        if not deduplicated:
            return 0

        updated = 0
        inserted = 0
        city_ids = list(deduplicated.keys())

        async with self.cities_repository.transaction():
            existing_rows = await self.cities_repository.search(id_in=city_ids)
            existing_ids = {row['id'] for row in existing_rows}

            for city_id, city_payload in deduplicated.items():
                db_payload = {
                    'country_code': city_payload['country_code'],
                    'name': city_payload['name'],
                    'name_normalized': city_payload['name_normalized'],
                    'latitude': city_payload.get('latitude'),
                    'longitude': city_payload.get('longitude'),
                    'population': city_payload.get('population'),
                    'labels': self._serialize_json_field(city_payload.get('labels')),
                    'meta': self._serialize_json_field(city_payload.get('meta')),
                }
                if city_id in existing_ids:
                    await self.cities_repository.update(db_payload, id=city_id)
                    updated += 1
                else:
                    await self.cities_repository.create(id=city_id, **db_payload)
                    inserted += 1

        return inserted + updated

    def _extract_query(self, filters: dict[str, Any], keys: tuple[str, ...]) -> str | None:
        for key in keys:
            value = filters.get(key)
            if not isinstance(value, str):
                continue
            cleaned = value.replace('%', ' ').replace('_', ' ').strip()
            if cleaned:
                return cleaned
        return None

    def _extract_country_codes(self, filters: dict[str, Any], keys: tuple[str, ...]) -> list[str]:
        codes: list[str] = []
        for key in keys:
            value = filters.get(key)
            if isinstance(value, str):
                code = value.upper().strip()
                if len(code) == 2:
                    codes.append(code)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        code = item.upper().strip()
                        if len(code) == 2:
                            codes.append(code)

        deduplicated: list[str] = []
        seen: set[str] = set()
        for code in codes:
            if code in seen:
                continue
            deduplicated.append(code)
            seen.add(code)
        return deduplicated

    def _extract_country_code(self, filters: dict[str, Any]) -> str | None:
        codes = self._extract_country_codes(filters, keys=('country_code', 'country_code_in'))
        return codes[0] if codes else None

    def _serialize_json_field(self, value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return json.dumps(value)
