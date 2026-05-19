import asyncio
import hashlib
import hmac
import json
import logging
import secrets
from datetime import timedelta
from typing import Any
from urllib.parse import parse_qsl
from uuid import UUID

import arrow

from app.models import OtpRequestStatus
from app.repositories import RowNotFoundError
from app.repositories.otp_requests import OtpRequestsRepository
from app.repositories.telegram_users import TelegramUsersRepository
from app.repositories.users import UsersRepository
from app.repositories.yandex_users import YandexUsersRepository
from app.services.exceptions import AppError, AuthenticationError, CountdownError
from app.services.otp_sender import OtpSenderProtocol
from app.services.yandex_auth import YandexAuthClient
from helpers.security import decode_token, encode_token
from settings import AppSettings

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        users_repository: UsersRepository,
        telegram_users_repository: TelegramUsersRepository,
        yandex_users_repository: YandexUsersRepository,
        otp_requests_repository: OtpRequestsRepository,
        otp_sender: OtpSenderProtocol,
        yandex_auth_client: YandexAuthClient,
        settings: AppSettings,
    ):
        self.users_repository = users_repository
        self.telegram_users_repository = telegram_users_repository
        self.yandex_users_repository = yandex_users_repository
        self.otp_requests_repository = otp_requests_repository
        self.otp_sender = otp_sender
        self.yandex_auth_client = yandex_auth_client
        self.settings = settings

    async def request_otp(self, contact: str) -> dict[str, str]:
        otp_settings = self.settings.otp

        try:
            async with self.otp_requests_repository.transaction():
                latest = await self.otp_requests_repository.get_latest_by_contact_for_update(contact)
                if latest:
                    allowed_after = arrow.get(latest['created']).shift(seconds=otp_settings.otp_rate_limit_seconds)
                    if allowed_after > arrow.utcnow():
                        raise CountdownError(
                            {
                                'error': 'Please wait before requesting a new code',
                                'retry_after': (allowed_after - arrow.utcnow()).seconds,
                            }
                        )

                code = str(secrets.randbelow(10**6)).zfill(6)
                expires_at = arrow.utcnow().shift(minutes=otp_settings.otp_ttl_minutes).datetime
                code_hash = hashlib.sha256(code.encode()).hexdigest()
                record = await self.otp_requests_repository.create(
                    contact=contact,
                    code_hash=code_hash,
                    expires_at=expires_at,
                    status=OtpRequestStatus.SENT,
                )
            try:
                await self.otp_sender.send(contact=contact, code=code)
            except Exception:  # noqa: BLE001
                await self.otp_requests_repository.update_status(record['id'], OtpRequestStatus.FAILED)
                raise
        except CountdownError:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.exception('Failed to send OTP')
            raise AppError('Failed to send OTP') from exc

        return {'otp_id': str(record['id']), 'message': 'OTP sent'}

    async def verify_otp(self, otp_id: UUID, code: str) -> dict[str, str]:
        otp_settings = self.settings.otp
        user: dict[str, Any] | None = None
        invalid_code = False

        async with self.users_repository.transaction():
            try:
                record = await self.otp_requests_repository.get_by_id_for_update(otp_id)
            except RowNotFoundError as exc:
                raise AuthenticationError('Invalid or expired OTP') from exc

            if record['status'] != OtpRequestStatus.SENT:
                raise AuthenticationError('Invalid or expired OTP')

            if arrow.get(record['expires_at']) <= arrow.utcnow():
                raise AuthenticationError('OTP has expired')

            if record['attempts'] >= otp_settings.otp_max_attempts:
                raise AuthenticationError('Too many incorrect attempts')

            code_hash = hashlib.sha256(code.encode()).hexdigest()
            if code_hash != record['code_hash'] and code != otp_settings.otp_mock_code:
                await self.otp_requests_repository.increment_attempts(otp_id)
                invalid_code = True
            else:
                user = await self.users_repository.get_by_email(record['contact'])
                if not user:
                    user = await self.users_repository.create(email=record['contact'])
                await self.otp_requests_repository.update_status(otp_id, OtpRequestStatus.DONE)

        if invalid_code:
            raise AuthenticationError('Invalid code')

        if not user:
            raise AuthenticationError('Invalid or expired OTP')

        return self._issue_tokens(user['id'])

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
            user_id=str(user_id),
            token_type='access',
            secret=auth_settings.jwt_secret,
            algorithm=auth_settings.jwt_algorithm,
            ttl=timedelta(minutes=auth_settings.access_token_ttl_minutes),
        )

    def _encode_refresh_token(self, user_id: UUID) -> str:
        auth_settings = self.settings.auth
        return encode_token(
            user_id=str(user_id),
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

    def verify_telegram_app_hash(self, init_data: str) -> bool:
        params = dict(parse_qsl(init_data, keep_blank_values=True))
        received_hash = params.pop('hash', '')
        data_check_string = '\n'.join(f'{k}={v}' for k, v in sorted(params.items()))
        secret_key = hmac.new(
            key=b'WebAppData',
            msg=self.settings.auth.telegram_bot_token.encode(),
            digestmod=hashlib.sha256,
        ).digest()
        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(calculated_hash, received_hash)

    async def login_via_telegram_app(self, init_data: str) -> dict[str, str]:
        params = dict(parse_qsl(init_data, keep_blank_values=True))
        await self.check_telegram_constraint({'auth_date': int(params['auth_date'])})

        verifies = await asyncio.to_thread(self.verify_telegram_app_hash, init_data)
        if not verifies:
            raise AuthenticationError('Invalid telegram app hash')

        user_data = json.loads(params['user'])
        telegram_id = user_data['id']

        user = await self.users_repository.get_user_by_telegram_user_id(telegram_id)
        if not user:
            async with self.users_repository.transaction():
                await self.telegram_users_repository.create(
                    telegram_id=telegram_id,
                    username=user_data.get('username'),
                    first_name=user_data.get('first_name'),
                    last_name=user_data.get('last_name'),
                    language_code=user_data.get('language_code'),
                    photo_url=user_data.get('photo_url'),
                )
                user = await self.users_repository.create(
                    telegram_user_id=telegram_id,
                    username=user_data.get('username'),
                    first_name=user_data.get('first_name'),
                    last_name=user_data.get('last_name'),
                )

        return self._issue_tokens(user['id'])

    async def login_via_telegram(self, telegram_data: dict[str, Any]) -> dict[str, str]:
        await self.check_telegram_constraint(telegram_data)
        verifies = await asyncio.to_thread(self.verify_telegram_hash, telegram_data)
        if not verifies:
            raise AuthenticationError('Invalid telegram hash')
        user = await self.users_repository.get_user_by_telegram_user_id(telegram_data['id'])
        if not user:
            async with self.users_repository.transaction():
                await self.telegram_users_repository.create(
                    telegram_id=telegram_data['id'],
                    username=telegram_data.get('username'),
                    first_name=telegram_data.get('first_name'),
                    last_name=telegram_data.get('last_name'),
                    language_code=telegram_data.get('language_code'),
                    photo_url=telegram_data.get('photo_url'),
                )
                user = await self.users_repository.create(
                    telegram_user_id=telegram_data['id'],
                    username=telegram_data.get('username'),
                    first_name=telegram_data.get('first_name'),
                    last_name=telegram_data.get('last_name'),
                )

        return self._issue_tokens(user['id'])

    async def login_via_yandex(
        self,
        *,
        code: str,
        redirect_uri: str | None = None,
        code_verifier: str | None = None,
    ) -> dict[str, str]:
        profile = await self.yandex_auth_client.get_user_info(
            code=code,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier,
        )
        yandex_id = str(profile['id'])
        yandex_profile = self._normalize_yandex_profile(profile)
        email = self._first_string(profile.get('default_email'), profile.get('email'))
        user = await self.users_repository.get_user_by_yandex_user_id(yandex_id)

        if not user:
            async with self.users_repository.transaction():
                await self.yandex_users_repository.upsert_profile(**yandex_profile)
                user = await self._get_or_create_yandex_user(yandex_id=yandex_id, email=email, profile=profile)
        else:
            await self.yandex_users_repository.upsert_profile(**yandex_profile)

        return self._issue_tokens(user['id'])

    async def _get_or_create_yandex_user(
        self,
        *,
        yandex_id: str,
        email: str | None,
        profile: dict[str, Any],
    ) -> dict[str, Any]:
        user = await self.users_repository.get_by_email(email) if email else None
        if user:
            linked_yandex_id = user.get('yandex_user_id')
            if linked_yandex_id and linked_yandex_id != yandex_id:
                raise AuthenticationError('Email is already linked to another Yandex account')
            return await self.users_repository.update_by_id(user['id'], yandex_user_id=yandex_id)

        return await self.users_repository.create(
            yandex_user_id=yandex_id,
            email=email,
            username=self._first_string(profile.get('login'), profile.get('display_name')),
            first_name=self._first_string(profile.get('first_name')),
            last_name=self._first_string(profile.get('last_name')),
        )

    def _normalize_yandex_profile(self, profile: dict[str, Any]) -> dict[str, Any]:
        return {
            'yandex_id': str(profile['id']),
            'login': self._first_string(profile.get('login')),
            'default_email': self._first_string(profile.get('default_email'), profile.get('email')),
            'first_name': self._first_string(profile.get('first_name')),
            'last_name': self._first_string(profile.get('last_name')),
            'display_name': self._first_string(profile.get('display_name')),
            'real_name': self._first_string(profile.get('real_name')),
            'default_avatar_id': self._first_string(profile.get('default_avatar_id')),
            'client_id': self._first_string(profile.get('client_id')),
            'psuid': self._first_string(profile.get('psuid')),
        }

    def _first_string(self, *values: Any) -> str | None:
        for value in values:
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None
