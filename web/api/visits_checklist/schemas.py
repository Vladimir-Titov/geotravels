from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models import CheckListStatus


@dataclass(eq=False)
class BaseListRequest:
    limit: int = field(default=100)
    offset: int = field(default=0)

    def to_repo_filters(self) -> dict[str, Any]:
        return {name: value for name, value in vars(self).items() if value is not None}


@dataclass(eq=False)
class VisitsChecklistListRequest(BaseListRequest):
    id: UUID | None = field(default=None)
    id_ne: UUID | None = field(default=None)
    id_in: list[UUID] | None = field(default=None)
    id_notin: list[UUID] | None = field(default=None)

    visit_id: UUID | None = field(default=None)
    visit_id_ne: UUID | None = field(default=None)
    visit_id_in: list[UUID] | None = field(default=None)
    visit_id_notin: list[UUID] | None = field(default=None)

    content: str | None = field(default=None)
    content_ne: str | None = field(default=None)
    content_like: str | None = field(default=None)
    content_ilike: str | None = field(default=None)

    status: CheckListStatus | None = field(default=None)
    status_ne: CheckListStatus | None = field(default=None)
    status_in: list[CheckListStatus] | None = field(default=None)
    status_notin: list[CheckListStatus] | None = field(default=None)

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


class CreateVisitChecklistRequest(BaseModel):
    visit_id: UUID
    content: str = Field(min_length=1)


class UpdateVisitChecklistRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    content: str | None = Field(default=None, min_length=1)
    status: CheckListStatus | None = None


class VisitChecklistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    visit_id: UUID
    content: str
    status: CheckListStatus
    user_id: UUID
    created: datetime
    updated: datetime


class VisitsChecklistListResponse(BaseModel):
    items: list[VisitChecklistResponse]
    pagination: PaginationResponse
