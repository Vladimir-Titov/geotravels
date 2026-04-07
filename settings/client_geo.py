from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings

from settings.base import COMMON_MODEL_CONFIG


class ClientGeoSettings(BaseSettings):
    model_config = COMMON_MODEL_CONFIG

    client_auth_header: str = 'X-Client-Token'
    client_auth_token: str = 'tripmark-client-token'
    client_rate_limit_requests: int = Field(default=60, ge=1)
    client_rate_limit_window_seconds: int = Field(default=60, ge=1)

    geonames_username: str | None = None
    geonames_base_url: str = 'https://api.geonames.org'
    geonames_timeout_seconds: float = Field(default=5.0, gt=0)
