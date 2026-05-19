from pydantic import Field
from pydantic_settings import BaseSettings

from settings.base import COMMON_MODEL_CONFIG


class AuthSettings(BaseSettings):
    model_config = COMMON_MODEL_CONFIG

    jwt_secret: str = Field(min_length=8)
    jwt_algorithm: str
    access_token_ttl_minutes: int
    refresh_token_ttl_days: int

    telegram_bot_token: str
    telegram_auth_date_ttl_hours: int = 24

    yandex_client_id: str | None = None
    yandex_client_secret: str | None = None
    yandex_oauth_token_url: str = 'https://oauth.yandex.ru/token'
    yandex_user_info_url: str = 'https://login.yandex.ru/info'
    yandex_auth_timeout_seconds: float = 5.0
