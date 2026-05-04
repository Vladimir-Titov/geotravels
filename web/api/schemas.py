from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from litestar.datastructures import UploadFile
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.tables import CheckListStatus, FileVisibility, VisitStatus, VisitVisibility


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


def _normalize_client_geo_lang(value: str | None) -> str:
    if not isinstance(value, str):
        return 'en'
    lang = value.strip().casefold().split('-', maxsplit=1)[0]
    return lang if lang in {'en', 'ru'} else 'en'


@dataclass(eq=False)
class ClientGeoCountriesListRequest(CountriesListRequest):
    lang: str | None = field(default=None)

    def to_repo_filters(self) -> dict[str, Any]:
        filters = super().to_repo_filters()
        filters.pop('lang', None)
        return filters

    @property
    def normalized_lang(self) -> str:
        return _normalize_client_geo_lang(self.lang)


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
class ClientGeoCitiesListRequest(CitiesListRequest):
    lang: str | None = field(default=None)

    def to_repo_filters(self) -> dict[str, Any]:
        filters = super().to_repo_filters()
        filters.pop('lang', None)
        return filters

    @property
    def normalized_lang(self) -> str:
        return _normalize_client_geo_lang(self.lang)


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

    city_id: UUID | None = field(default=None)
    city_id_ne: UUID | None = field(default=None)
    city_id_in: list[UUID] | None = field(default=None)
    city_id_notin: list[UUID] | None = field(default=None)

    date_from: date | None = field(default=None)
    date_from_ne: date | None = field(default=None)
    date_from_lt: date | None = field(default=None)
    date_from_le: date | None = field(default=None)
    date_from_gt: date | None = field(default=None)
    date_from_ge: date | None = field(default=None)
    date_from_in: list[date] | None = field(default=None)
    date_from_notin: list[date] | None = field(default=None)

    date_to: date | None = field(default=None)
    date_to_ne: date | None = field(default=None)
    date_to_lt: date | None = field(default=None)
    date_to_le: date | None = field(default=None)
    date_to_gt: date | None = field(default=None)
    date_to_ge: date | None = field(default=None)
    date_to_in: list[date] | None = field(default=None)
    date_to_notin: list[date] | None = field(default=None)

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


class ClientGeoCountryResponse(CountryResponse):
    display_name: str


class ClientGeoCountriesListResponse(BaseModel):
    items: list[ClientGeoCountryResponse]
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


class ClientGeoCityResponse(CityResponse):
    display_name: str


class ClientGeoCitiesListResponse(BaseModel):
    items: list[ClientGeoCityResponse]
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
    model_config = ConfigDict(extra='forbid')

    country_code: str = Field(min_length=2, max_length=2)
    title: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = None
    visibility: VisitVisibility = VisitVisibility.PRIVATE
    status: VisitStatus = VisitStatus.VISITED
    date_from: date | None = None
    date_to: date | None = None
    city_ids: list[UUID] | None = None
    cover_file_id: UUID | None = None

    city_id: UUID | None = None  # backward compatibility (visit-v1)


class UpdateVisitRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    title: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = None
    visibility: VisitVisibility | None = None
    status: VisitStatus | None = None
    date_from: date | None = None
    date_to: date | None = None
    city_ids: list[UUID] | None = None
    cover_file_id: UUID | None = None

    city_id: UUID | None = None  # backward compatibility (visit-v1)


class VisitEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    country_code: str
    title: str
    description: str | None = None
    visibility: VisitVisibility
    status: VisitStatus
    date_from: date | None = None
    date_to: date | None = None
    city_ids: list[UUID] = Field(default_factory=list)
    cover_file_id: UUID | None = None

    city_id: UUID | None = None
    created: datetime
    updated: datetime


class VisitsListResponse(BaseModel):
    items: list[VisitEventResponse]
    pagination: PaginationResponse


class VisitCardResponse(BaseModel):
    id: UUID
    status: VisitStatus
    title: str
    country_code: str
    country_name: str | None = None
    city_id: UUID | None = None
    city_name: str | None = None
    date_from: date | None = None
    date_to: date | None = None
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


class VisitDetailsVisitResponse(VisitEventResponse):
    country_name: str | None = None
    city_name: str | None = None
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


class VisitDetailsCityResponse(BaseModel):
    id: UUID
    name: str
    country_code: str


class VisitDetailsResponse(BaseModel):
    visit: VisitDetailsVisitResponse
    photos: list[VisitDetailsPhotoResponse]
    checklist: list[VisitChecklistResponse]
    places: list[VisitPlaceResponse]
    cities: list[VisitDetailsCityResponse]


class VisitsPlacesListResponse(BaseModel):
    items: list[VisitPlaceResponse]
    pagination: PaginationResponse


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


class FollowRequest(BaseModel):
    following_id: UUID


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
    }
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
    is_cover: bool = False


class FilesListResponse(BaseModel):
    items: list[VisitFileResponse]
    pagination: PaginationResponse


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
