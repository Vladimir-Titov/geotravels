from typing import Any
from uuid import UUID, uuid7

from app.models.tables import users
from app.repositories.base import BaseEntityDBRepository


class UsersRepository(BaseEntityDBRepository):
    entity = users

    async def get_by_email(self, email: str) -> dict[str, Any] | None:
        return await self.search_first_row(email=email)

    async def create(self, **data) -> dict[str, Any]:
        return await super().create(id=uuid7(), **data)

    async def get_user_by_telegram_user_id(self, telegram_user_id: int) -> dict[str, Any] | None:
        return await self.search_first_row(telegram_user_id=telegram_user_id)

    def _normalize_row(self, row: dict[str, Any]) -> dict[str, Any]:
        if isinstance(row.get('id'), str):
            row['id'] = UUID(row['id'])
        return row
