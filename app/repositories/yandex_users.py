from typing import Any

from app.models import yandex_users
from app.repositories.base import BaseEntityDBRepository


class YandexUsersRepository(BaseEntityDBRepository):
    entity = yandex_users

    async def get_by_yandex_id(self, yandex_id: str) -> dict[str, Any] | None:
        return await self.search_first_row(yandex_id=yandex_id)

    async def upsert_profile(self, **profile: Any) -> dict[str, Any]:
        yandex_id = profile['yandex_id']
        existing = await self.get_by_yandex_id(yandex_id)
        if existing:
            rows = await self.update(profile, yandex_id=yandex_id)
            return rows[0]
        return await self.create(**profile)
