from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


@dataclass(eq=False)
class BaseListRequest:
    limit: int = field(default=100)
    offset: int = field(default=0)

    def to_repo_filters(self) -> dict[str, Any]:
        return {name: value for name, value in vars(self).items() if value is not None}


@dataclass(eq=False)
class FilesListRequest(BaseListRequest):
    visit_id: UUID | None = field(default=None)


class PaginationResponse(BaseModel):
    limit: int | None
    offset: int
    total: int


class UpdateFileRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=64)


class VisitFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    file_url: str
    filename: str | None = None
    file_type: str | None = None
    visit_id: UUID | None = None
    user_id: UUID | None = None
    is_private: bool
    is_cover: bool = False


class FilesListResponse(BaseModel):
    items: list[VisitFileResponse]
    pagination: PaginationResponse
