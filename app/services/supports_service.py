from asyncpg import ForeignKeyViolationError

from app.repositories import SupportTicketsRepository
from app.services.exceptions import UnprocessableEntityError


class SupportsService:
    def __init__(self, support_tickets_repository: SupportTicketsRepository):
        self.support_tickets_repository = support_tickets_repository

    async def create_support_ticket(self, **data):
        try:
            return await self.support_tickets_repository.create(**data)
        except ForeignKeyViolationError as e:
            raise UnprocessableEntityError('User not found')
