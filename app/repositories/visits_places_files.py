from __future__ import annotations

from typing import Any
from uuid import UUID, uuid7

from sqlalchemy import select

from app.models.tables import visits_places, visits_places_files
from app.repositories.base import BaseEntityDBRepository


class VisitsPlacesFilesRepository(BaseEntityDBRepository):
    entity = visits_places_files
    base_search_query = select(
        visits_places_files.c.id,
        visits_places_files.c.visit_place_id,
        visits_places_files.c.file_id,
        visits_places_files.c.created,
        visits_places_files.c.updated,
        visits_places.c.user_id,
        visits_places.c.visit_id,
    ).select_from(
        visits_places_files.join(
            visits_places,
            visits_places_files.c.visit_place_id == visits_places.c.id,
        )
    )

    async def create(
        self,
        visit_place_id: UUID,
        file_id: UUID,
    ) -> dict[str, Any]:
        return await super().create(
            id=uuid7(),
            visit_place_id=visit_place_id,
            file_id=file_id,
        )

    def _normalize_row(self, row: dict[str, Any]) -> dict[str, Any]:
        if isinstance(row.get('id'), str):
            row['id'] = UUID(row['id'])
        if isinstance(row.get('visit_place_id'), str):
            row['visit_place_id'] = UUID(row['visit_place_id'])
        if isinstance(row.get('file_id'), str):
            row['file_id'] = UUID(row['file_id'])
        if isinstance(row.get('user_id'), str):
            row['user_id'] = UUID(row['user_id'])
        if isinstance(row.get('visit_id'), str):
            row['visit_id'] = UUID(row['visit_id'])
        return row
