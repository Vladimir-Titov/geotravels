from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


@dataclass(eq=False)
class BaseListRequest:
    limit: int = field(default=100)
    offset: int = field(default=0)

    def to_repo_filters(self) -> dict[str, Any]:
        return {name: value for name, value in vars(self).items() if value is not None}


@dataclass(eq=False)
class UsersListRequest(BaseListRequest):
    id: UUID | None = field(default=None)
    id_ne: UUID | None = field(default=None)
    id_in: list[UUID] | None = field(default=None)
    id_notin: list[UUID] | None = field(default=None)

    email: str | None = field(default=None)
    email_ne: str | None = field(default=None)
    email_in: list[str] | None = field(default=None)
    email_notin: list[str] | None = field(default=None)
    email_like: str | None = field(default=None)
    email_ilike: str | None = field(default=None)

    first_name: str | None = field(default=None)
    first_name_ne: str | None = field(default=None)
    first_name_in: list[str] | None = field(default=None)
    first_name_notin: list[str] | None = field(default=None)
    first_name_like: str | None = field(default=None)
    first_name_ilike: str | None = field(default=None)

    last_name: str | None = field(default=None)
    last_name_ne: str | None = field(default=None)
    last_name_in: list[str] | None = field(default=None)
    last_name_notin: list[str] | None = field(default=None)
    last_name_like: str | None = field(default=None)
    last_name_ilike: str | None = field(default=None)

    username: str | None = field(default=None)
    username_ne: str | None = field(default=None)
    username_in: list[str] | None = field(default=None)
    username_notin: list[str] | None = field(default=None)
    username_like: str | None = field(default=None)
    username_ilike: str | None = field(default=None)

    telegram_user_id: int | None = field(default=None)
    telegram_user_id_ne: int | None = field(default=None)
    telegram_user_id_lt: int | None = field(default=None)
    telegram_user_id_le: int | None = field(default=None)
    telegram_user_id_gt: int | None = field(default=None)
    telegram_user_id_ge: int | None = field(default=None)
    telegram_user_id_in: list[int] | None = field(default=None)
    telegram_user_id_notin: list[int] | None = field(default=None)

    created: datetime | None = field(default=None)
    created_ne: datetime | None = field(default=None)
    created_lt: datetime | None = field(default=None)
    created_le: datetime | None = field(default=None)
    created_gt: datetime | None = field(default=None)
    created_ge: datetime | None = field(default=None)
    created_in: list[datetime] | None = field(default=None)
    created_notin: list[datetime] | None = field(default=None)

    updated: datetime | None = field(default=None)
    updated_ne: datetime | None = field(default=None)
    updated_lt: datetime | None = field(default=None)
    updated_le: datetime | None = field(default=None)
    updated_gt: datetime | None = field(default=None)
    updated_ge: datetime | None = field(default=None)
    updated_in: list[datetime] | None = field(default=None)
    updated_notin: list[datetime] | None = field(default=None)


class PaginationResponse(BaseModel):
    limit: int | None
    offset: int
    total: int


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    telegram_user_id: int | None = None
    created: datetime
    updated: datetime


class UsersListResponse(BaseModel):
    items: list[UserResponse]
    pagination: PaginationResponse
