from __future__ import annotations

import logging

from litestar import Router, post
from litestar.exceptions import HTTPException

from app.services.auth import AuthService
from app.services.exceptions import ServiceError
from web.api.schemas import (
    AccessTokenResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TelegramAuthRequest,
    TokenPairResponse,
)

logger = logging.getLogger(__name__)


@post('/register', tags=['auth'])
async def register(data: RegisterRequest, auth_service: AuthService) -> TokenPairResponse:
    try:
        payload = await auth_service.register(email=str(data.email), password=data.password)
        return TokenPairResponse(**payload)
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@post('/login', tags=['auth'])
async def login(data: LoginRequest, auth_service: AuthService) -> TokenPairResponse:
    try:
        payload = await auth_service.login(email=str(data.email), password=data.password)
        return TokenPairResponse(**payload)
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


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


auth_router = Router(path='/api/v1/auth', route_handlers=[register, login, refresh, telegram_login])
