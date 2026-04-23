from __future__ import annotations

from typing import Any
from uuid import UUID, uuid7

from app.models.tables import visits_places
from app.repositories.base import BaseEntityDBRepository


class VisitsPlacesRepository(BaseEntityDBRepository):
    entity = visits_places

    async def create(
        self,
        visit_id: UUID,
        user_id: UUID,
        title: str,
        is_visited: bool = False,
    ) -> dict[str, Any]:
        return await super().create(
            id=uuid7(),
            visit_id=visit_id,
            user_id=user_id,
            title=title,
            is_visited=is_visited,
        )

    def _normalize_row(self, row: dict[str, Any]) -> dict[str, Any]:
        if isinstance(row.get('id'), str):
            row['id'] = UUID(row['id'])
        if isinstance(row.get('visit_id'), str):
            row['visit_id'] = UUID(row['visit_id'])
        if isinstance(row.get('user_id'), str):
            row['user_id'] = UUID(row['user_id'])
        return row
