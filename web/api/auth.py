from __future__ import annotations

import logging
from uuid import UUID

from litestar import Router, post
from litestar.exceptions import HTTPException

from app.services.auth import AuthService
from app.services.exceptions import ServiceError
from web.api.schemas import (
    AccessTokenResponse,
    OtpRequestResponse,
    OtpRequestSchema,
    OtpVerifyRequest,
    RefreshRequest,
    TelegramAuthRequest,
    TokenPairResponse,
)

logger = logging.getLogger(__name__)


@post('/otp/request', tags=['auth'])
async def otp_request(data: OtpRequestSchema, auth_service: AuthService) -> OtpRequestResponse:
    try:
        payload = await auth_service.request_otp(contact=data.contact)
        return OtpRequestResponse(**payload)
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@post('/otp/verify', tags=['auth'])
async def otp_verify(data: OtpVerifyRequest, auth_service: AuthService) -> TokenPairResponse:
    try:
        payload = await auth_service.verify_otp(otp_id=UUID(data.otp_id), code=data.code)
        return TokenPairResponse(**payload)
    except (ValueError, ServiceError) as exc:
        status_code = exc.status_code if isinstance(exc, ServiceError) else 400
        detail = exc.detail if isinstance(exc, ServiceError) else 'Invalid otp_id format'
        raise HTTPException(status_code=status_code, detail=detail) from exc


@post('/refresh', tags=['auth'])
async def refresh(data: RefreshRequest, auth_service: AuthService) -> AccessTokenResponse:
    try:
        payload = await auth_service.refresh(refresh_token=data.refresh_token)
        return AccessTokenResponse(**payload)
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@post('/telegram', tags=['auth'])
async def telegram_login(data: TelegramAuthRequest, auth_service: AuthService) -> TokenPairResponse:
    try:
        payload = await auth_service.login_via_telegram(telegram_data=data.model_dump(exclude_none=True))
        return TokenPairResponse(**payload)
    except ServiceError as exc:
        logger.exception(f'Telegram login failed: {exc}')
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


auth_router = Router(path='/api/v1/auth', route_handlers=[otp_request, otp_verify, refresh, telegram_login])
