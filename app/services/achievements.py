from __future__ import annotations

from typing import Any
from uuid import UUID

from app.repositories.achievements import AchievementsRepository
from app.repositories.base import PaginatedResponse
from app.repositories.users_achievements import UsersAchievementsRepository


class AchievementsService:
    def __init__(
        self,
        achievements_repository: AchievementsRepository,
        users_achievements_repository: UsersAchievementsRepository,
    ):
        self.achievements_repository = achievements_repository
        self.users_achievements_repository = users_achievements_repository

    async def list_achievements(self, limit: int, offset: int, **filters: Any) -> PaginatedResponse:
        return await self.achievements_repository.paginated_search(limit=limit, offset=offset, **filters)

    async def list_user_achievements(
        self,
        user_id: UUID,
        limit: int,
        offset: int,
        **filters: Any,
    ) -> PaginatedResponse:
        return await self.users_achievements_repository.paginated_search(
            limit=limit,
            offset=offset,
            user_id=user_id,
            **filters,
        )
