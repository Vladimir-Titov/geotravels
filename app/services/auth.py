from __future__ import annotations

from datetime import timedelta
from typing import Any
from uuid import UUID

from app.repositories.users import UsersRepository
from app.services.exceptions import AuthenticationError, ConflictError
from helpers.security import decode_token, encode_token, hash_password, verify_password
from settings import AppSettings


class AuthService:
    def __init__(
        self,
        users_repository: UsersRepository,
        settings: AppSettings,
    ):
        self.users_repository = users_repository
        self.settings = settings

    async def register(self, email: str, password: str) -> dict[str, str]:
        async with self.users_repository.transaction():
            existing_user = await self.users_repository.get_by_email(email)
            if existing_user:
                raise ConflictError('User with this email already exists')

            user = await self.users_repository.create(
                email=email,
                password_hash=hash_password(password),
            )

        return self._issue_tokens(user_id=user['id'])

    async def login(self, email: str, password: str) -> dict[str, str]:
        user = await self.users_repository.get_by_email(email)

        if not user or not verify_password(password, user['password_hash']):
            raise AuthenticationError('Invalid credentials')

        return self._issue_tokens(user_id=user['id'])

    async def refresh(self, refresh_token: str) -> dict[str, str]:
        payload = self._decode_token(refresh_token, expected_type='refresh')
        user_id = UUID(payload['sub'])
        user = await self.users_repository.get_by_id(user_id)

        if not user:
            raise AuthenticationError('User not found')

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
        return encode_token(
            subject=str(user_id),
            token_type='access',
            secret=self.settings.jwt_secret,
            algorithm=self.settings.jwt_algorithm,
            ttl=timedelta(minutes=self.settings.access_token_ttl_minutes),
        )

    def _encode_refresh_token(self, user_id: UUID) -> str:
        return encode_token(
            subject=str(user_id),
            token_type='refresh',
            secret=self.settings.jwt_secret,
            algorithm=self.settings.jwt_algorithm,
            ttl=timedelta(days=self.settings.refresh_token_ttl_days),
        )

    def _decode_token(self, token: str, expected_type: str) -> dict[str, Any]:
        try:
            payload = decode_token(
                token=token,
                secret=self.settings.jwt_secret,
                algorithm=self.settings.jwt_algorithm,
            )
        except ValueError as exc:
            raise AuthenticationError(str(exc)) from exc

        if payload['type'] != expected_type:
            raise AuthenticationError('Invalid token type')

        return payload
