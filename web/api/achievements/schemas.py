from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from web.api.base import BaseListRequest, PaginationResponse


@dataclass(eq=False)
class AchievementsListRequest(BaseListRequest):
    order_by: str | None = field(default=None)

    id: UUID | None = field(default=None)
    id_ne: UUID | None = field(default=None)
    id_in: list[UUID] | None = field(default=None)
    id_notin: list[UUID] | None = field(default=None)

    title: str | None = field(default=None)
    title_ne: str | None = field(default=None)
    title_in: list[str] | None = field(default=None)
    title_notin: list[str] | None = field(default=None)
    title_like: str | None = field(default=None)
    title_ilike: str | None = field(default=None)

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


@dataclass(eq=False)
class UserAchievementsListRequest(AchievementsListRequest):
    complete_at: datetime | None = field(default=None)
    complete_at_ne: datetime | None = field(default=None)
    complete_at_lt: datetime | None = field(default=None)
    complete_at_le: datetime | None = field(default=None)
    complete_at_gt: datetime | None = field(default=None)
    complete_at_ge: datetime | None = field(default=None)
    complete_at_in: list[datetime] | None = field(default=None)
    complete_at_notin: list[datetime] | None = field(default=None)


class AchievementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str
    logo_url: str | None = None
    created: datetime
    updated: datetime


class AchievementsListResponse(BaseModel):
    items: list[AchievementResponse]
    pagination: PaginationResponse


class EarnedAchievementResponse(AchievementResponse):
    complete_at: datetime


class EarnedAchievementsListResponse(BaseModel):
    items: list[EarnedAchievementResponse]
    pagination: PaginationResponse
