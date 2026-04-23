from __future__ import annotations

from typing import Any
from uuid import UUID

from app.repositories.base import PaginatedResponse
from app.repositories.files import FilesRepository
from app.repositories.visits_places import VisitsPlacesRepository
from app.repositories.visits_places_files import VisitsPlacesFilesRepository
from app.services.exceptions import ConflictError, NotFoundError, ServiceError


class VisitsPlacesFilesService:
    def __init__(
        self,
        visits_places_files_repository: VisitsPlacesFilesRepository,
        visits_places_repository: VisitsPlacesRepository,
        files_repository: FilesRepository,
    ):
        self.visits_places_files_repository = visits_places_files_repository
        self.visits_places_repository = visits_places_repository
        self.files_repository = files_repository

    async def _get_place_or_raise(self, place_id: UUID, user_id: UUID) -> dict[str, Any]:
        place = await self.visits_places_repository.search_first_row(id=place_id, user_id=user_id)
        if not place:
            raise NotFoundError('Visit place not found')
        return place

    async def _get_relation_or_raise(self, relation_id: UUID, user_id: UUID) -> dict[str, Any]:
        relation = await self.visits_places_files_repository.search_first_row(id=relation_id, user_id=user_id)
        if not relation:
            raise NotFoundError('Visit place file relation not found')
        return relation

    async def create_relation(self, user_id: UUID, visit_place_id: UUID, file_id: UUID) -> dict[str, Any]:
        place = await self._get_place_or_raise(place_id=visit_place_id, user_id=user_id)
        file = await self.files_repository.get_owned_file(file_id=file_id, user_id=user_id)
        if not file:
            raise NotFoundError('File not found')
        if file.get('visit_id') != place['visit_id']:
            raise ServiceError('file_id must reference a file attached to the same visit as visit_place_id')

        try:
            return await self.visits_places_files_repository.create(
                visit_place_id=visit_place_id,
                file_id=file_id,
            )
        except Exception as exc:  # noqa: BLE001
            existing = await self.visits_places_files_repository.search_first_row(
                visit_place_id=visit_place_id,
                file_id=file_id,
                user_id=user_id,
            )
            if existing:
                raise ConflictError('File is already linked to this visit place') from exc
            raise

    async def list_relations(self, user_id: UUID, limit: int, offset: int, **filters: Any) -> PaginatedResponse:
        return await self.visits_places_files_repository.paginated_search(
            order_by=['-created', '-id'],
            limit=limit,
            offset=offset,
            user_id=user_id,
            **filters,
        )

    async def get_relation_by_id(self, relation_id: UUID, user_id: UUID) -> dict[str, Any]:
        return await self._get_relation_or_raise(relation_id=relation_id, user_id=user_id)

    async def delete_relation_by_id(self, relation_id: UUID, user_id: UUID) -> None:
        await self._get_relation_or_raise(relation_id=relation_id, user_id=user_id)
        await self.visits_places_files_repository.delete_by_id(entity_id=relation_id)
