from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OtpRequestSchema(BaseModel):
    contact: str


class OtpRequestResponse(BaseModel):
    otp_id: str
    message: str


class OtpVerifyRequest(BaseModel):
    otp_id: str
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


class CountryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    iso_a2: str
    name: str


class CountriesListResponse(BaseModel):
    items: list[CountryResponse]


class MarkVisitRequest(BaseModel):
    country_code: str = Field(min_length=2, max_length=2)
    trip_date: date | None = None


class VisitEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    country_code: str
    marked_at: datetime
    trip_date: date | None = None


class VisitsResponse(BaseModel):
    visits: list[VisitEventResponse]
    visited_country_codes: list[str]


class TelegramAuthRequest(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str


class HealthcheckResponse(BaseModel):
    status: bool
