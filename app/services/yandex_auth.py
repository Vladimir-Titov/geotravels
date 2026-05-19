import logging
from typing import Any

from aiohttp import ClientSession

from app.services.exceptions import AuthenticationError

logger = logging.getLogger(__name__)


class YandexAuthClient:
    def __init__(
        self,
        *,
        client_id: str | None,
        client_secret: str | None,
        token_url: str,
        user_info_url: str,
        timeout_seconds: float,
        session: ClientSession,
    ):
        self.client_id = client_id.strip() if client_id else None
        self.client_secret = client_secret.strip() if client_secret else None
        self.token_url = token_url
        self.user_info_url = user_info_url
        self.timeout_seconds = timeout_seconds
        self.session = session

    async def get_user_info(
        self,
        *,
        code: str,
        redirect_uri: str | None = None,
        code_verifier: str | None = None,
    ) -> dict[str, Any]:
        access_token = await self._exchange_code(
            code=code,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier,
        )
        return await self._fetch_user_info(access_token)

    async def _exchange_code(
        self,
        *,
        code: str,
        redirect_uri: str | None,
        code_verifier: str | None,
    ) -> str:
        if not self.client_id or not self.client_secret:
            raise AuthenticationError('Yandex auth is not configured')

        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        if redirect_uri:
            data['redirect_uri'] = redirect_uri
        if code_verifier:
            data['code_verifier'] = code_verifier

        try:
            async with self.session.post(self.token_url, data=data, timeout=self.timeout_seconds) as response:
                if response.status >= 400:
                    logger.info('Yandex token exchange failed with status %s', response.status)
                    raise AuthenticationError('Yandex token exchange failed')
                payload = await response.json()
        except AuthenticationError:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.warning('Yandex token exchange request failed: %s', exc)
            raise AuthenticationError('Yandex token exchange failed') from exc

        access_token = payload.get('access_token')
        if not isinstance(access_token, str) or not access_token:
            raise AuthenticationError('Yandex token exchange failed')

        return access_token

    async def _fetch_user_info(self, access_token: str) -> dict[str, Any]:
        try:
            async with self.session.get(
                self.user_info_url,
                headers={'Authorization': f'OAuth {access_token}'},
                params={'format': 'json'},
                timeout=self.timeout_seconds,
            ) as response:
                if response.status >= 400:
                    logger.info('Yandex user info request failed with status %s', response.status)
                    raise AuthenticationError('Yandex user info request failed')
                payload = await response.json()
        except AuthenticationError:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.warning('Yandex user info request failed: %s', exc)
            raise AuthenticationError('Yandex user info request failed') from exc

        if not isinstance(payload, dict) or not payload.get('id'):
            raise AuthenticationError('Yandex user info request failed')

        return payload
