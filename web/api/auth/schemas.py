from uuid import UUID

from pydantic import BaseModel


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
