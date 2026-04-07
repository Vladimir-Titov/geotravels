from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any
from uuid import UUID

from app.models.tables import cities
from app.repositories.base import BaseEntityDBRepository


class CitiesRepository(BaseEntityDBRepository):
    entity = cities

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

    async def upsert_from_geonames(self, payload: list[Mapping[str, Any]]) -> int:
        if not payload:
            return 0

        deduplicated: dict[UUID, dict[str, Any]] = {}
        for item in payload:
            city_id = item.get('id')
            if not isinstance(city_id, UUID):
                continue
            deduplicated[city_id] = dict(item)

        if not deduplicated:
            return 0

        city_ids = list(deduplicated.keys())
        updated = 0
        inserted = 0

        async with self.transaction():
            existing_rows = await self.search(id_in=city_ids)
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
                    await self.update(db_payload, id=city_id)
                    updated += 1
                else:
                    await self.create(id=city_id, **db_payload)
                    inserted += 1

        return inserted + updated

    def _serialize_json_field(self, value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return json.dumps(value)
