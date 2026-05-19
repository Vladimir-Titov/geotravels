from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any
from uuid import UUID

from litestar.datastructures import UploadFile
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import CheckListStatus, FileVisibility, VisitStatus, VisitVisibility


@dataclass(eq=False)
class BaseListRequest:
    limit: int = field(default=100)
    offset: int = field(default=0)

    def to_repo_filters(self) -> dict[str, Any]:
        return {name: value for name, value in vars(self).items() if value is not None}


@dataclass(eq=False)
class VisitsListRequest(BaseListRequest):
    id: UUID | None = field(default=None)
    id_ne: UUID | None = field(default=None)
    id_in: list[UUID] | None = field(default=None)
    id_notin: list[UUID] | None = field(default=None)

    country_code: str | None = field(default=None)
    country_code_ne: str | None = field(default=None)
    country_code_in: list[str] | None = field(default=None)
    country_code_notin: list[str] | None = field(default=None)
    country_code_like: str | None = field(default=None)
    country_code_ilike: str | None = field(default=None)

    title: str | None = field(default=None)
    title_ne: str | None = field(default=None)
    title_like: str | None = field(default=None)
    title_ilike: str | None = field(default=None)

    visibility: VisitVisibility | None = field(default=None)
    visibility_ne: VisitVisibility | None = field(default=None)
    visibility_in: list[VisitVisibility] | None = field(default=None)
    visibility_notin: list[VisitVisibility] | None = field(default=None)

    status: VisitStatus | None = field(default=None)
    status_ne: VisitStatus | None = field(default=None)
    status_in: list[VisitStatus] | None = field(default=None)
    status_notin: list[VisitStatus] | None = field(default=None)

    city_ids_in: list[UUID] | None = field(default=None)

    trip_start: date | None = field(default=None)
    trip_start_ne: date | None = field(default=None)
    trip_start_lt: date | None = field(default=None)
    trip_start_le: date | None = field(default=None)
    trip_start_gt: date | None = field(default=None)
    trip_start_ge: date | None = field(default=None)
    trip_start_in: list[date] | None = field(default=None)
    trip_start_notin: list[date] | None = field(default=None)

    trip_end: date | None = field(default=None)
    trip_end_ne: date | None = field(default=None)
    trip_end_lt: date | None = field(default=None)
    trip_end_le: date | None = field(default=None)
    trip_end_gt: date | None = field(default=None)
    trip_end_ge: date | None = field(default=None)
    trip_end_in: list[date] | None = field(default=None)
    trip_end_notin: list[date] | None = field(default=None)

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


class MarkVisitRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    country_code: str = Field(min_length=2, max_length=2)
    title: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = None
    visibility: VisitVisibility = VisitVisibility.PRIVATE
    status: VisitStatus = VisitStatus.VISITED
    trip_start: date | None = None
    trip_end: date | None = None
    city_ids: list[UUID] | None = None
    cover_file_id: UUID | None = None


class UpdateVisitRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    title: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = None
    visibility: VisitVisibility | None = None
    status: VisitStatus | None = None
    trip_start: date | None = None
    trip_end: date | None = None
    city_ids: list[UUID] | None = None
    cover_file_id: UUID | None = None


class VisitEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    country_code: str
    title: str
    description: str | None = None
    visibility: VisitVisibility
    status: VisitStatus
    trip_start: date | None = None
    trip_end: date | None = None
    city_ids: list[UUID] = Field(default_factory=list)
    cover_file_id: UUID | None = None

    created: datetime
    updated: datetime


class VisitsListResponse(BaseModel):
    items: list[VisitEventResponse]
    pagination: PaginationResponse


class VisitCityResponse(BaseModel):
    id: UUID
    name: str
    country_code: str


class VisitCardResponse(BaseModel):
    id: UUID
    status: VisitStatus
    title: str
    country_code: str
    country_name: str | None = None
    cities: list[VisitCityResponse] = Field(default_factory=list)
    trip_start: date | None = None
    trip_end: date | None = None
    cover_url: str | None = None
    photos_count: int
    checklist_total: int
    checklist_done: int
    places_total: int
    places_visited: int


class VisitCardsListResponse(BaseModel):
    items: list[VisitCardResponse]
    pagination: PaginationResponse


class TripsByCountryResponse(BaseModel):
    country_name: str | None = None
    trips_count: int


class FavoriteCityResponse(BaseModel):
    city_id: UUID
    city_name: str
    visits_count: int


class VisitStatisticsResponse(BaseModel):
    visited_count: int
    planned_count: int
    countries_count: int
    cities_count: int
    repeated_countries_count: int
    favorite_city: FavoriteCityResponse | None = None
    trips_by_country: list[TripsByCountryResponse]


class VisitChecklistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    visit_id: UUID
    content: str
    status: CheckListStatus
    user_id: UUID
    created: datetime
    updated: datetime


class VisitPlaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    visit_id: UUID
    title: str
    user_id: UUID
    is_visited: bool
    created: datetime
    updated: datetime


class VisitDetailsVisitResponse(VisitEventResponse):
    country_name: str | None = None
    cover_url: str | None = None


class VisitDetailsPhotoResponse(BaseModel):
    id: UUID
    file_url: str
    thumbnail_url: str | None = None
    preview_url: str | None = None
    filename: str | None = None
    file_type: str | None = None
    is_private: bool
    is_cover: bool


class VisitDetailsResponse(BaseModel):
    visit: VisitDetailsVisitResponse
    photos: list[VisitDetailsPhotoResponse]
    checklist: list[VisitChecklistResponse]
    places: list[VisitPlaceResponse]
    cities: list[VisitCityResponse]


ALLOWED_UPLOAD_IMAGE_TYPES = frozenset(
    {
        'image/jpeg',
        'image/jpg',
        'image/png',
        'image/webp',
        'image/heic',
        'image/heif',
        'image/heic-sequence',
        'image/heif-sequence',
        'image/x-heic',
        'image/x-heif',
    },
)


class UploadFileRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    file: UploadFile
    filename: str | None = None
    file_type: str | None = None
    visibility: FileVisibility = FileVisibility.PRIVATE

    @field_validator('file')
    @classmethod
    def validate_file_content_type(cls, file: UploadFile) -> UploadFile:
        content_type = (file.content_type or '').split(';', maxsplit=1)[0].strip().lower()
        if content_type not in ALLOWED_UPLOAD_IMAGE_TYPES:
            allowed_types = ', '.join(sorted(ALLOWED_UPLOAD_IMAGE_TYPES))
            raise ValueError(f'file content type must be one of: {allowed_types}')
        return file


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
