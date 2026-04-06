from __future__ import annotations

from typing import Any
from uuid import UUID, uuid7

from app.models.tables import achievements
from app.repositories.base import BaseEntityDBRepository


class AchievementsRepository(BaseEntityDBRepository):
    entity = achievements

    async def create(self, title: str, description: str, logo_url: str | None = None) -> dict[str, Any]:
        return await super().create(
            id=uuid7(),
            title=title,
            description=description,
            logo_url=logo_url,
        )

    def _normalize_row(self, row: dict[str, Any]) -> dict[str, Any]:
        if isinstance(row.get('id'), str):
            row['id'] = UUID(row['id'])
        return row
