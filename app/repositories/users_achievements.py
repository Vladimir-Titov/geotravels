from datetime import datetime
from typing import Any
from uuid import UUID, uuid7

from sqlalchemy import select

from app.models.tables import achievements, users_achievements
from app.repositories.base import BaseEntityDBRepository


class UsersAchievementsRepository(BaseEntityDBRepository):
    entity = users_achievements
    base_search_query = select(
        achievements.c.id,
        achievements.c.title,
        achievements.c.description,
        achievements.c.logo_url,
        achievements.c.created,
        achievements.c.updated,
        users_achievements.c.user_id,
        users_achievements.c.complete_at,
    ).select_from(users_achievements.join(achievements, users_achievements.c.achievements_id == achievements.c.id))

    async def create(
        self,
        user_id: UUID,
        achievements_id: UUID,
        complete_at: datetime | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            'id': uuid7(),
            'user_id': user_id,
            'achievements_id': achievements_id,
        }
        if complete_at is not None:
            payload['complete_at'] = complete_at
        return await super().create(**payload)

    def _normalize_row(self, row: dict[str, Any]) -> dict[str, Any]:
        if isinstance(row.get('id'), str):
            row['id'] = UUID(row['id'])
        if isinstance(row.get('user_id'), str):
            row['user_id'] = UUID(row['user_id'])
        return row
