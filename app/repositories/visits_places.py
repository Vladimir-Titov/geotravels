from collections.abc import Mapping
from typing import Any
from uuid import UUID, uuid7

from app.models import visits_places
from app.repositories.base import BaseEntityDBRepository


class VisitsPlacesRepository(BaseEntityDBRepository):
    entity = visits_places

    async def create(
        self,
        visit_id: UUID,
        user_id: UUID,
        title: str,
        address: str | None = None,
        description: str | None = None,
        is_visited: bool = False,
    ) -> dict[str, Any]:
        return await super().create(
            id=uuid7(),
            visit_id=visit_id,
            user_id=user_id,
            title=title,
            address=address,
            description=description,
            is_visited=is_visited,
        )

    async def create_many_for_visit(self, payload: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
        return await self.create_many([{**item, 'id': uuid7()} for item in payload])

    def _normalize_row(self, row: dict[str, Any]) -> dict[str, Any]:
        if isinstance(row.get('id'), str):
            row['id'] = UUID(row['id'])
        if isinstance(row.get('visit_id'), str):
            row['visit_id'] = UUID(row['visit_id'])
        if isinstance(row.get('user_id'), str):
            row['user_id'] = UUID(row['user_id'])
        return row
