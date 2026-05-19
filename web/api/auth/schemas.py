from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class OtpRequestSchema(BaseModel):
    contact: EmailStr


class OtpRequestResponse(BaseModel):
    otp_id: UUID
    message: str


class OtpVerifyRequest(BaseModel):
    otp_id: UUID
    code: str = Field(min_length=6, max_length=6, pattern=r'^\d{6}$')


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


class YandexAuthRequest(BaseModel):
    code: str = Field(min_length=1)
    redirect_uri: str | None = None
    code_verifier: str | None = None
