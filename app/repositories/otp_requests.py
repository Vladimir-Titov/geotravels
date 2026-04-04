from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from app.models.tables import otp_requests
from app.repositories.base import BaseEntityDBRepository, RowNotFoundError


class OtpRequestsRepository(BaseEntityDBRepository):
    entity = otp_requests

    async def create(self, **data: Any) -> dict[str, Any]:
        return await super().create(id=uuid4(), **data)

    async def get_latest_by_contact(self, contact: str) -> dict[str, Any] | None:
        return await self.search_first_row(order_by='-created', contact=contact)

    async def get_latest_by_contact_for_update(self, contact: str) -> dict[str, Any] | None:
        rows = await self.search_for_update(order_by='-created', limit=1, contact=contact)
        return rows[0] if rows else None

    async def increment_attempts(self, otp_id: UUID) -> None:
        return await self.update_by_id(otp_id, attempts=self.entity.c.attempts + 1)

    async def delete_by_id(self, otp_id: UUID) -> None:
        return await super().delete_by_id(otp_id)

    async def get_by_id_for_update(self, otp_id: UUID) -> dict[str, Any]:
        rows = await self.search_for_update(id=otp_id, limit=1)
        if not rows:
            raise RowNotFoundError()
        return rows[0]

    async def update_status(self, otp_id: UUID, status: str) -> None:
        return await self.update_by_id(otp_id, status=status)
