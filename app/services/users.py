from typing import Any

from app.repositories.base import PaginatedResponse
from app.repositories.users import UsersRepository


class UsersService:
    def __init__(self, users_repository: UsersRepository):
        self.users_repository = users_repository

    async def list_users(self, limit: int, offset: int, **filters: Any) -> PaginatedResponse:
        return await self.users_repository.paginated_search(
            order_by=['-created', '-id'],
            limit=limit,
            offset=offset,
            **filters,
        )
