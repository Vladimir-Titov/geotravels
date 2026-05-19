from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from web.api.base import BaseListRequest, PaginationResponse


@dataclass(eq=False)
class VisitsPlacesListRequest(BaseListRequest):
    id: UUID | None = field(default=None)
    id_ne: UUID | None = field(default=None)
    id_in: list[UUID] | None = field(default=None)
    id_notin: list[UUID] | None = field(default=None)

    visit_id: UUID | None = field(default=None)
    visit_id_ne: UUID | None = field(default=None)
    visit_id_in: list[UUID] | None = field(default=None)
    visit_id_notin: list[UUID] | None = field(default=None)

    title: str | None = field(default=None)
    title_ne: str | None = field(default=None)
    title_like: str | None = field(default=None)
    title_ilike: str | None = field(default=None)

    is_visited: bool | None = field(default=None)
    is_visited_ne: bool | None = field(default=None)

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


class CreateVisitPlaceRequest(BaseModel):
    visit_id: UUID
    title: str = Field(min_length=1, max_length=255)


class UpdateVisitPlaceRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    title: str | None = Field(default=None, min_length=1, max_length=255)
    is_visited: bool | None = None


class VisitPlaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    visit_id: UUID
    title: str
    user_id: UUID
    is_visited: bool
    created: datetime
    updated: datetime


class VisitsPlacesListResponse(BaseModel):
    items: list[VisitPlaceResponse]
    pagination: PaginationResponse
