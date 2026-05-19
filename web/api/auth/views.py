from litestar import Router, post

from app.services.auth import AuthService
from web.api.auth.schemas import (
    AccessTokenResponse,
    OtpRequestResponse,
    OtpRequestSchema,
    OtpVerifyRequest,
    RefreshRequest,
    TelegramAppAuthRequest,
    TelegramAuthRequest,
    TokenPairResponse,
)


@post('/otp/request', tags=['auth'])
async def otp_request(data: OtpRequestSchema, auth_service: AuthService) -> OtpRequestResponse:
    payload = await auth_service.request_otp(contact=str(data.contact))
    return OtpRequestResponse(**payload)


@post('/otp/verify', tags=['auth'])
async def otp_verify(data: OtpVerifyRequest, auth_service: AuthService) -> TokenPairResponse:
    payload = await auth_service.verify_otp(otp_id=data.otp_id, code=data.code)
    return TokenPairResponse(**payload)


@post('/refresh', tags=['auth'])
async def refresh(data: RefreshRequest, auth_service: AuthService) -> AccessTokenResponse:
    payload = await auth_service.refresh(refresh_token=data.refresh_token)
    return AccessTokenResponse(**payload)


@post('/telegram', tags=['auth'])
async def telegram_login(data: TelegramAuthRequest, auth_service: AuthService) -> TokenPairResponse:
    payload = await auth_service.login_via_telegram(telegram_data=data.model_dump(exclude_none=True))
    return TokenPairResponse(**payload)


@post('/telegram_app', tags=['auth'])
async def telegram_app_login(data: TelegramAppAuthRequest, auth_service: AuthService) -> TokenPairResponse:
    payload = await auth_service.login_via_telegram_app(init_data=data.init_data)
    return TokenPairResponse(**payload)


auth_router = Router(
    path='/api/v1/auth', route_handlers=[otp_request, otp_verify, refresh, telegram_login, telegram_app_login]
)
