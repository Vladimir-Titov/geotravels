from typing import Any
from uuid import UUID

from app.repositories.base import PaginatedResponse
from app.repositories.visits import VisitsRepository
from app.repositories.visits_places import VisitsPlacesRepository
from app.services.exceptions import ConflictError, NotFoundError, ServiceError


class VisitsPlacesService:
    def __init__(
        self,
        visits_places_repository: VisitsPlacesRepository,
        visits_repository: VisitsRepository,
    ):
        self.visits_places_repository = visits_places_repository
        self.visits_repository = visits_repository

    @staticmethod
    def _normalize_title(title: str) -> str:
        normalized = title.strip()
        if not normalized:
            raise ServiceError('title cannot be empty')
        if len(normalized) > 255:
            raise ServiceError('title is too long, max length is 255')
        return normalized

    async def _ensure_visit_owned(self, visit_id: UUID, user_id: UUID) -> None:
        visit = await self.visits_repository.search_first_row(id=visit_id, user_id=user_id)
        if not visit:
            raise NotFoundError('Visit not found')

    async def _get_place_or_raise(self, place_id: UUID, user_id: UUID) -> dict[str, Any]:
        place = await self.visits_places_repository.search_first_row(id=place_id, user_id=user_id)
        if not place:
            raise NotFoundError('Visit place not found')
        return place

    async def create_place(self, user_id: UUID, visit_id: UUID, title: str) -> dict[str, Any]:
        await self._ensure_visit_owned(visit_id=visit_id, user_id=user_id)
        normalized_title = self._normalize_title(title)

        try:
            return await self.visits_places_repository.create(
                visit_id=visit_id,
                user_id=user_id,
                title=normalized_title,
                is_visited=False,
            )
        except Exception as exc:  # noqa: BLE001
            existing = await self.visits_places_repository.search_first_row(
                visit_id=visit_id,
                user_id=user_id,
                title=normalized_title,
            )
            if existing:
                raise ConflictError('Visit place with this title already exists') from exc
            raise

    async def list_places(self, user_id: UUID, limit: int, offset: int, **filters: Any) -> PaginatedResponse:
        return await self.visits_places_repository.paginated_search(
            order_by=['-created', '-id'],
            limit=limit,
            offset=offset,
            user_id=user_id,
            **filters,
        )

    async def get_place_by_id(self, place_id: UUID, user_id: UUID) -> dict[str, Any]:
        return await self._get_place_or_raise(place_id=place_id, user_id=user_id)

    async def update_place_by_id(self, place_id: UUID, user_id: UUID, **payload: Any) -> dict[str, Any]:
        current = await self._get_place_or_raise(place_id=place_id, user_id=user_id)
        update_payload = dict(payload)

        normalized_title: str | None = None
        if 'title' in update_payload:
            normalized_title = self._normalize_title(update_payload['title'])
            update_payload['title'] = normalized_title

        try:
            return await self.visits_places_repository.update_by_id(entity_id=place_id, **update_payload)
        except Exception as exc:  # noqa: BLE001
            if normalized_title is not None:
                existing = await self.visits_places_repository.search_first_row(
                    visit_id=current['visit_id'],
                    user_id=user_id,
                    title=normalized_title,
                )
                if existing and existing['id'] != place_id:
                    raise ConflictError('Visit place with this title already exists') from exc
            raise

    async def delete_place_by_id(self, place_id: UUID, user_id: UUID) -> None:
        await self._get_place_or_raise(place_id=place_id, user_id=user_id)
        await self.visits_places_repository.delete_by_id(entity_id=place_id)
