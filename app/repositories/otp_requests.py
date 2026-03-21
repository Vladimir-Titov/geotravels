from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import delete

from app.models.tables import otp_requests_table
from app.repositories.base import BaseEntityDBRepository


class OtpRequestsRepository(BaseEntityDBRepository):
    entity = otp_requests_table

    async def create(self, **data: Any) -> dict[str, Any]:
        return await super().create(id=uuid4(), **data)

    async def get_latest_by_contact(self, contact: str) -> dict[str, Any] | None:
        return await self.search_first_row(order_by='-created', contact=contact)

    async def get_latest_by_contact_for_update(self, contact: str) -> dict[str, Any] | None:
        rows = await self.search_for_update(order_by='-created', limit=1, contact=contact)
        return rows[0] if rows else None

    async def increment_attempts(self, otp_id: UUID) -> None:
        query = self.entity.update().where(self.entity.c.id == otp_id).values(attempts=self.entity.c.attempts + 1)
        async with self.connection() as conn:
            await conn.execute(query)

    async def delete_by_id(self, otp_id: UUID) -> None:
        query = delete(self.entity).where(self.entity.c.id == otp_id)
        async with self.connection() as conn:
            await conn.execute(query)
