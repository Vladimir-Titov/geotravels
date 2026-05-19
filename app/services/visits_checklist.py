from typing import Any
from uuid import UUID

from app.models import CheckListStatus
from app.repositories.base import PaginatedResponse
from app.repositories.visits import VisitsRepository
from app.repositories.visits_checklist import VisitsChecklistRepository
from app.services.exceptions import NotFoundError, ServiceError


class VisitsChecklistService:
    ALLOWED_STATUSES = {
        CheckListStatus.TO_DO,
        CheckListStatus.DONE,
    }

    def __init__(
        self,
        visits_checklist_repository: VisitsChecklistRepository,
        visits_repository: VisitsRepository,
    ):
        self.visits_checklist_repository = visits_checklist_repository
        self.visits_repository = visits_repository

    @staticmethod
    def _normalize_content(content: str) -> str:
        normalized = content.strip()
        if not normalized:
            raise ServiceError('content cannot be empty')
        return normalized

    @classmethod
    def _normalize_status(cls, status: CheckListStatus | None) -> CheckListStatus:
        if status is None:
            return CheckListStatus.TO_DO
        if status not in cls.ALLOWED_STATUSES:
            allowed_statuses = ', '.join(item.value for item in CheckListStatus)
            raise ServiceError(f'status must be one of: {allowed_statuses}')
        return status

    async def _ensure_visit_owned(self, visit_id: UUID, user_id: UUID) -> None:
        visit = await self.visits_repository.search_first_row(id=visit_id, user_id=user_id)
        if not visit:
            raise NotFoundError('Visit not found')

    async def _get_item_or_raise(self, checklist_id: UUID, user_id: UUID) -> dict[str, Any]:
        item = await self.visits_checklist_repository.search_first_row(id=checklist_id, user_id=user_id)
        if not item:
            raise NotFoundError('Visit checklist item not found')
        return item

    async def create_item(self, user_id: UUID, visit_id: UUID, content: str) -> dict[str, Any]:
        await self._ensure_visit_owned(visit_id=visit_id, user_id=user_id)
        return await self.visits_checklist_repository.create(
            visit_id=visit_id,
            user_id=user_id,
            content=self._normalize_content(content),
            status=CheckListStatus.TO_DO,
        )

    async def list_items(self, user_id: UUID, limit: int, offset: int, **filters: Any) -> PaginatedResponse:
        return await self.visits_checklist_repository.paginated_search(
            order_by=['-created', '-id'],
            limit=limit,
            offset=offset,
            user_id=user_id,
            **filters,
        )

    async def get_item_by_id(self, checklist_id: UUID, user_id: UUID) -> dict[str, Any]:
        return await self._get_item_or_raise(checklist_id=checklist_id, user_id=user_id)

    async def update_item_by_id(self, checklist_id: UUID, user_id: UUID, **payload: Any) -> dict[str, Any]:
        await self._get_item_or_raise(checklist_id=checklist_id, user_id=user_id)

        update_payload = dict(payload)
        if 'content' in update_payload:
            update_payload['content'] = self._normalize_content(update_payload['content'])
        if 'status' in update_payload:
            update_payload['status'] = self._normalize_status(update_payload['status'])

        return await self.visits_checklist_repository.update_by_id(entity_id=checklist_id, **update_payload)

    async def delete_item_by_id(self, checklist_id: UUID, user_id: UUID) -> None:
        await self._get_item_or_raise(checklist_id=checklist_id, user_id=user_id)
        await self.visits_checklist_repository.delete_by_id(entity_id=checklist_id)
