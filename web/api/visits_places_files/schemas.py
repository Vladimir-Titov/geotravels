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
class VisitsPlacesFilesListRequest(BaseListRequest):
    id: UUID | None = field(default=None)
    id_ne: UUID | None = field(default=None)
    id_in: list[UUID] | None = field(default=None)
    id_notin: list[UUID] | None = field(default=None)

    visit_place_id: UUID | None = field(default=None)
    visit_place_id_ne: UUID | None = field(default=None)
    visit_place_id_in: list[UUID] | None = field(default=None)
    visit_place_id_notin: list[UUID] | None = field(default=None)

    file_id: UUID | None = field(default=None)
    file_id_ne: UUID | None = field(default=None)
    file_id_in: list[UUID] | None = field(default=None)
    file_id_notin: list[UUID] | None = field(default=None)

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


class CreateVisitPlaceFileRequest(BaseModel):
    visit_place_id: UUID
    file_id: UUID


class VisitPlaceFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    visit_place_id: UUID
    file_id: UUID
    created: datetime
    updated: datetime


class VisitsPlacesFilesListResponse(BaseModel):
    items: list[VisitPlaceFileResponse]
    pagination: PaginationResponse
