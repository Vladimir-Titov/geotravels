from __future__ import annotations

from typing import Any
from uuid import UUID, uuid7

from sqlalchemy import func, select

from app.models.tables import followers
from app.repositories.base import BaseEntityDBRepository


class FollowersRepository(BaseEntityDBRepository):
    entity = followers

    async def create(self, follower_id: UUID, following_id: UUID) -> dict[str, Any]:
        return await super().create(
            id=uuid7(),
            follower_id=follower_id,
            following_id=following_id,
        )

    async def get_relation(self, follower_id: UUID, following_id: UUID) -> dict[str, Any] | None:
        return await self.search_first_row(follower_id=follower_id, following_id=following_id)

    async def count_followers_for_user(self, user_id: UUID) -> int:
        query = select(func.count()).select_from(followers).where(followers.c.following_id == user_id)
        value = await self.fetchval(query)
        return int(value or 0)

    def _normalize_row(self, row: dict[str, Any]) -> dict[str, Any]:
        if isinstance(row.get('id'), str):
            row['id'] = UUID(row['id'])
        if isinstance(row.get('follower_id'), str):
            row['follower_id'] = UUID(row['follower_id'])
        if isinstance(row.get('following_id'), str):
            row['following_id'] = UUID(row['following_id'])
        return row
