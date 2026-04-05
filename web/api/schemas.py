from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any
from uuid import UUID

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
