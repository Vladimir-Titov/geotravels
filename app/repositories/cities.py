from __future__ import annotations

import json
from typing import Any

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
