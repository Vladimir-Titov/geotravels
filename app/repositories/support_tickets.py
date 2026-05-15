from typing import Any
from uuid import uuid7

from app.models import support_tickets
from app.repositories import BaseEntityDBRepository


class SupportTicketsRepository(BaseEntityDBRepository):
    entity = support_tickets

    async def create(self, **data) -> dict[str, Any]:
        return await super().create(id=uuid7(), **data)
