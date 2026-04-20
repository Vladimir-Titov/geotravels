from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID

from litestar.datastructures import UploadFile
from pydantic import BaseModel, ConfigDict, Field


class OtpRequestSchema(BaseModel):
    contact: str


class OtpRequestResponse(BaseModel):
    otp_id: str
    message: str


class OtpVerifyRequest(BaseModel):
    otp_id: UUID
    code: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str


@dataclass(eq=False)
class BaseListRequest:
    limit: int = field(default=100)
    offset: int = field(default=0)

    def to_repo_filters(self) -> dict[str, Any]:
        return {name: value for name, value in vars(self).items() if value is not None}


@dataclass(eq=False)
class CountriesListRequest(BaseListRequest):
    iso_a2: str | None = field(default=None)
    iso_a2_ne: str | None = field(default=None)
    iso_a2_in: list[str] | None = field(default=None)
    iso_a2_notin: list[str] | None = field(default=None)
    iso_a2_like: str | None = field(default=None)
    iso_a2_ilike: str | None = field(default=None)

    name: str | None = field(default=None)
    name_ne: str | None = field(default=None)
    name_in: list[str] | None = field(default=None)
    name_notin: list[str] | None = field(default=None)
    name_like: str | None = field(default=None)
    name_ilike: str | None = field(default=None)

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
class CitiesListRequest(BaseListRequest):
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

    name: str | None = field(default=None)
    name_ne: str | None = field(default=None)
    name_in: list[str] | None = field(default=None)
    name_notin: list[str] | None = field(default=None)
    name_like: str | None = field(default=None)
    name_ilike: str | None = field(default=None)

    name_normalized: str | None = field(default=None)
    name_normalized_ne: str | None = field(default=None)
    name_normalized_in: list[str] | None = field(default=None)
    name_normalized_notin: list[str] | None = field(default=None)
    name_normalized_like: str | None = field(default=None)
    name_normalized_ilike: str | None = field(default=None)

    latitude: float | None = field(default=None)
    latitude_ne: float | None = field(default=None)
    latitude_lt: float | None = field(default=None)
    latitude_le: float | None = field(default=None)
    latitude_gt: float | None = field(default=None)
    latitude_ge: float | None = field(default=None)
    latitude_in: list[float] | None = field(default=None)
    latitude_notin: list[float] | None = field(default=None)

    longitude: float | None = field(default=None)
    longitude_ne: float | None = field(default=None)
    longitude_lt: float | None = field(default=None)
    longitude_le: float | None = field(default=None)
    longitude_gt: float | None = field(default=None)
    longitude_ge: float | None = field(default=None)
    longitude_in: list[float] | None = field(default=None)
    longitude_notin: list[float] | None = field(default=None)

    population: int | None = field(default=None)
    population_ne: int | None = field(default=None)
    population_lt: int | None = field(default=None)
    population_le: int | None = field(default=None)
    population_gt: int | None = field(default=None)
    population_ge: int | None = field(default=None)
    population_in: list[int] | None = field(default=None)
    population_notin: list[int] | None = field(default=None)

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

    city_id: UUID | None = field(default=None)
    city_id_ne: UUID | None = field(default=None)
    city_id_in: list[UUID] | None = field(default=None)
    city_id_notin: list[UUID] | None = field(default=None)

    trip_date: date | None = field(default=None)
    trip_date_ne: date | None = field(default=None)
    trip_date_lt: date | None = field(default=None)
    trip_date_le: date | None = field(default=None)
    trip_date_gt: date | None = field(default=None)
    trip_date_ge: date | None = field(default=None)
    trip_date_in: list[date] | None = field(default=None)
    trip_date_notin: list[date] | None = field(default=None)

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
class FollowersListRequest(BaseListRequest):
    id: UUID | None = field(default=None)
    id_ne: UUID | None = field(default=None)
    id_in: list[UUID] | None = field(default=None)
    id_notin: list[UUID] | None = field(default=None)

    follower_id: UUID | None = field(default=None)
    follower_id_ne: UUID | None = field(default=None)
    follower_id_in: list[UUID] | None = field(default=None)
    follower_id_notin: list[UUID] | None = field(default=None)

    following_id: UUID | None = field(default=None)
    following_id_ne: UUID | None = field(default=None)
    following_id_in: list[UUID] | None = field(default=None)
    following_id_notin: list[UUID] | None = field(default=None)

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
class FilesListRequest(BaseListRequest):
    visit_id: UUID | None = field(default=None)


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


class PaginationResponse(BaseModel):
    limit: int | None
    offset: int
    total: int


class CountryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    iso_a2: str
    name: str
    labels: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None
    created: datetime
    updated: datetime


class CountriesListResponse(BaseModel):
    items: list[CountryResponse]
    pagination: PaginationResponse


class CityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    country_code: str
    name: str
    name_normalized: str
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    population: int | None = None
    labels: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None
    created: datetime
    updated: datetime


class CitiesListResponse(BaseModel):
    items: list[CityResponse]
    pagination: PaginationResponse


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


class MarkVisitRequest(BaseModel):
    country_code: str = Field(min_length=2, max_length=2)
    city_id: UUID | None = None
    trip_date: date | None = None


class UpdateVisitRequest(BaseModel):
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    city_id: UUID | None = None
    trip_date: date | None = None


class VisitEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    country_code: str
    city_id: UUID | None = None
    trip_date: date | None = None
    created: datetime
    updated: datetime


class VisitsListResponse(BaseModel):
    items: list[VisitEventResponse]
    pagination: PaginationResponse


class FollowRequest(BaseModel):
    following_id: UUID


class UploadFileRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    visit_id: UUID
    file: UploadFile
    filename: str | None = None
    file_type: str | None = None
    is_private: bool = False


class UpdateFileRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=64)


class FollowerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    follower_id: UUID
    following_id: UUID
    created: datetime
    updated: datetime


class FollowersListResponse(BaseModel):
    items: list[FollowerResponse]
    pagination: PaginationResponse


class VisitFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    file_url: str
    filename: str | None = None
    file_type: str | None = None
    visit_id: UUID | None = None
    user_id: UUID | None = None
    is_private: bool


class FilesListResponse(BaseModel):
    items: list[VisitFileResponse]
    pagination: PaginationResponse


class DashboardMeResponse(BaseModel):
    display_name: str
    username: str | None = None


class DashboardStatsResponse(BaseModel):
    countries_count: int
    cities_count: int
    stories_count: int


class DashboardMilestoneResponse(BaseModel):
    title: str
    description: str
    progress_percent: int
    current_value: int
    target_value: int


class DashboardRecapResponse(BaseModel):
    period: str
    title: str
    summary_line: str
    is_ready: bool
    share_url: str | None = None
    share_route: str | None = None


class DashboardRecentStoryLocationResponse(BaseModel):
    country_code: str
    country_name: str | None = None
    city_id: UUID | None = None
    city_name: str | None = None


class DashboardStoryCountersResponse(BaseModel):
    views: int | None = None
    likes: int | None = None
    comments: int | None = None


DashboardStoryVisibility = Literal['private', 'followers', 'public']


class DashboardRecentStoryResponse(BaseModel):
    id: UUID
    title: str
    excerpt: str | None = None
    visibility: DashboardStoryVisibility
    created_at: datetime
    location: DashboardRecentStoryLocationResponse
    cover: str | None = None
    counters: DashboardStoryCountersResponse


class DashboardInboxItemResponse(BaseModel):
    type: str
    text: str
    created_at: datetime
    is_read: bool


class DashboardInboxPreviewResponse(BaseModel):
    unread_count: int
    items: list[DashboardInboxItemResponse]


class DashboardMostVisitedItemResponse(BaseModel):
    country_name: str | None = None
    trips_count: int
    relative_bar_value: int


class DashboardResponse(BaseModel):
    me: DashboardMeResponse
    stats: DashboardStatsResponse
    next_milestone: DashboardMilestoneResponse
    recap: DashboardRecapResponse
    recent_stories: list[DashboardRecentStoryResponse]
    inbox_preview: DashboardInboxPreviewResponse
    most_visited: list[DashboardMostVisitedItemResponse]


class TelegramAuthRequest(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str


class TelegramAppAuthRequest(BaseModel):
    init_data: str


class HealthcheckResponse(BaseModel):
    status: bool
