import json
from collections.abc import Mapping
from typing import Any

from app.models.tables import countries
from app.repositories.base import BaseEntityDBRepository


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

    async def insert_missing(self, countries: list[dict[str, str]]) -> int:
        if not countries:
            return 0

        async with self.transaction():
            existing_rows = await self.search(order_by='iso_a2')
            existing_codes = {row['iso_a2'] for row in existing_rows}
            to_insert = [item for item in countries if item['iso_a2'] not in existing_codes]
            await self.create_many(to_insert)  # pyright: ignore[reportArgumentType]
            return len(to_insert)

    async def upsert_from_geonames(self, payload: list[Mapping[str, Any]]) -> int:
        if not payload:
            return 0

        deduplicated: dict[str, dict[str, Any]] = {}
        for item in payload:
            iso_a2 = str(item.get('iso_a2', '')).upper().strip()
            name = str(item.get('name', '')).strip()
            if len(iso_a2) != 2 or not name:
                continue
            deduplicated[iso_a2] = {
                'iso_a2': iso_a2,
                'name': name,
                'meta': item.get('meta'),
                'labels': item.get('labels'),
            }

        if not deduplicated:
            return 0

        updated = 0
        inserted = 0
        country_codes = list(deduplicated.keys())

        async with self.transaction():
            existing_rows = await self.search(iso_a2_in=country_codes)
            existing_codes = {row['iso_a2'] for row in existing_rows}

            for iso_a2, country_payload in deduplicated.items():
                db_payload = {
                    'name': country_payload['name'],
                    'meta': self._serialize_json_field(country_payload.get('meta')),
                    'labels': self._serialize_json_field(country_payload.get('labels')),
                }
                if iso_a2 in existing_codes:
                    await self.update(db_payload, iso_a2=iso_a2)
                    updated += 1
                else:
                    await self.create(iso_a2=iso_a2, **db_payload)
                    inserted += 1

        return inserted + updated

    def _serialize_json_field(self, value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return json.dumps(value)
