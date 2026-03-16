from __future__ import annotations

import asyncio
import hashlib
import hmac
import logging
from datetime import timedelta
from typing import Any
from uuid import UUID

import arrow

from app.repositories import RowNotFoundError
from app.repositories.users import UsersRepository
from app.services.exceptions import AppError, AuthenticationError, ConflictError
from helpers.security import decode_token, encode_token, hash_password, verify_password
from settings import AppSettings

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        users_repository: UsersRepository,
        settings: AppSettings,
    ):
        self.users_repository = users_repository
        self.settings = settings

    async def register(self, email: str, password: str) -> dict[str, str]:
        try:
            existing_user: dict[str, Any] | None = await self.users_repository.get_by_email(email)
            if existing_user:
                raise ConflictError('User with this email already exists')
            user = await self.users_repository.create(
                email=email,
                password_hash=hash_password(password),
            )
        except ConflictError:
            raise
        except Exception as exc:
            if self._is_unique_violation_error(exc):
                raise ConflictError('User with this email already exists') from exc
            raise AppError('Failed to register user') from exc

        return self._issue_tokens(user_id=user['id'])

    async def login(self, email: str, password: str) -> dict[str, str]:
        user = await self.users_repository.get_by_email(email)

        if not user or not verify_password(password, user['password_hash']):
            raise AuthenticationError('Invalid credentials')

        return self._issue_tokens(user_id=user['id'])

    async def refresh(self, refresh_token: str) -> dict[str, str]:
        payload = self._decode_token(refresh_token, expected_type='refresh')
        user_id = UUID(payload['sub'])
        try:
            await self.users_repository.get_by_id(user_id)
        except RowNotFoundError as exc:
            raise AuthenticationError('User not found') from exc

        access_token = self._encode_access_token(user_id=user_id)
        return {'access_token': access_token, 'token_type': 'bearer'}

    def get_user_id_from_access_token(self, access_token: str) -> UUID:
        payload = self._decode_token(access_token, expected_type='access')
        return UUID(payload['sub'])

    def _issue_tokens(self, user_id: UUID) -> dict[str, str]:
        return {
            'access_token': self._encode_access_token(user_id=user_id),
            'refresh_token': self._encode_refresh_token(user_id=user_id),
            'token_type': 'bearer',
        }

    def _encode_access_token(self, user_id: UUID) -> str:
        auth_settings = self.settings.auth
        return encode_token(
            subject=str(user_id),
            token_type='access',
            secret=auth_settings.jwt_secret,
            algorithm=auth_settings.jwt_algorithm,
            ttl=timedelta(minutes=auth_settings.access_token_ttl_minutes),
        )

    def _encode_refresh_token(self, user_id: UUID) -> str:
        auth_settings = self.settings.auth
        return encode_token(
            subject=str(user_id),
            token_type='refresh',
            secret=auth_settings.jwt_secret,
            algorithm=auth_settings.jwt_algorithm,
            ttl=timedelta(days=auth_settings.refresh_token_ttl_days),
        )

    def _decode_token(self, token: str, expected_type: str) -> dict[str, Any]:
        auth_settings = self.settings.auth
        try:
            payload = decode_token(
                token=token,
                secret=auth_settings.jwt_secret,
                algorithm=auth_settings.jwt_algorithm,
            )
        except ValueError as exc:
            raise AuthenticationError(str(exc)) from exc

        if payload['type'] != expected_type:
            raise AuthenticationError('Invalid token type')

        return payload

    def _is_unique_violation_error(self, exc: Exception) -> bool:
        current: BaseException | None = exc
        while current:
            text = str(current).lower()
            if 'duplicate key' in text or 'unique constraint' in text:
                return True
            current = current.__cause__ or current.__context__
        return False

    def verify_telegram_hash(self, telegram_data: dict[str, Any]) -> bool:
        secret_key = hashlib.sha256(self.settings.auth.telegram_bot_token.encode()).digest()
        telegram_hash = telegram_data.pop('hash')
        data_check_string = '\n'.join([f'{k}={v}' for k, v in sorted(telegram_data.items())])
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), digestmod=hashlib.sha256).hexdigest()
        return hmac.compare_digest(calculated_hash, telegram_hash)

    async def check_telegram_constraint(self, telegram_data: dict[str, Any]) -> None:
        auth_date = arrow.get(telegram_data['auth_date'])
        if auth_date.shift(hours=self.settings.auth.telegram_auth_date_ttl_hours) <= arrow.utcnow():
            raise AuthenticationError('Telegram auth date is too old')

    async def login_via_telegram(
        self,
        telegram_data: dict[str, Any],
    ) -> dict[str, str]:  # todo: make telegram_data like TypedDict
        await self.check_telegram_constraint(telegram_data)
        verifies_telegram_data = await asyncio.to_thread(self.verify_telegram_hash, telegram_data)
        if not verifies_telegram_data:
            raise AuthenticationError('Invalid telegram hash')
        user = await self.users_repository.get_user_by_telegram_id(telegram_data['id'])
        if not user:
            user = await self.users_repository.create(telegram_id=telegram_data['id'])
        return self._issue_tokens(user['id'])
