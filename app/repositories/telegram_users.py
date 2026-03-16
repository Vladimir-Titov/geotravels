from typing import Any

from app.models.tables import telegram_users
from app.repositories.base import BaseEntityDBRepository


class TelegramUsersRepository(BaseEntityDBRepository):
    entity = telegram_users

    async def get_by_telegram_id(self, telegram_id: int) -> dict[str, Any] | None:
        return await self.search_first_row(telegram_id=telegram_id)
