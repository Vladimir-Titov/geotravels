from __future__ import annotations

from typing import Any
from uuid import UUID

from app.repositories.base import PaginatedResponse, RowNotFoundError
from app.repositories.followers import FollowersRepository
from app.repositories.users import UsersRepository
from app.services.exceptions import ConflictError, NotFoundError, ServiceError


class FollowersService:
    def __init__(
        self,
        followers_repository: FollowersRepository,
        users_repository: UsersRepository,
    ):
        self.followers_repository = followers_repository
        self.users_repository = users_repository

    async def subscribe(self, follower_id: UUID, following_id: UUID) -> dict[str, Any]:
        if follower_id == following_id:
            raise ServiceError('Cannot follow yourself')

        await self._ensure_user_exists(user_id=following_id)

        existing_relation = await self.followers_repository.get_relation(
            follower_id=follower_id,
            following_id=following_id,
        )
        if existing_relation:
            raise ConflictError('Already following this user')

        return await self.followers_repository.create(
            follower_id=follower_id,
            following_id=following_id,
        )

    async def unsubscribe(self, follower_id: UUID, following_id: UUID) -> None:
        relation = await self.followers_repository.get_relation(
            follower_id=follower_id,
            following_id=following_id,
        )
        if not relation:
            raise NotFoundError('Follow relation not found')

        await self.followers_repository.delete_by_id(entity_id=relation['id'])

    async def list_followers(self, limit: int, offset: int, **filters: Any) -> PaginatedResponse:
        return await self.followers_repository.paginated_search(
            order_by=['-created', '-id'],
            limit=limit,
            offset=offset,
            **filters,
        )

    async def _ensure_user_exists(self, user_id: UUID) -> None:
        try:
            await self.users_repository.get_by_id(user_id)
        except RowNotFoundError as exc:
            raise NotFoundError('User not found') from exc
