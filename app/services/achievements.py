from __future__ import annotations

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

    async def list_achievements(self, limit: int, offset: int) -> PaginatedResponse:
        return await self.achievements_repository.paginated_search(
            order_by=['title', 'id'],
            limit=limit,
            offset=offset,
        )

    async def list_user_achievements(self, user_id: UUID, limit: int, offset: int) -> PaginatedResponse:
        return await self.users_achievements_repository.paginated_search(
            order_by=['-complete_at', 'id'],
            limit=limit,
            offset=offset,
            user_id=user_id,
        )
