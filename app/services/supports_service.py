from app.repositories import SupportTicketsRepository


class SupportsService:
    def __init__(self, support_tickets_repository: SupportTicketsRepository):
        self.support_tickets_repository = support_tickets_repository

    async def create_support_ticket(self, **data):
        return await self.support_tickets_repository.create(**data)
