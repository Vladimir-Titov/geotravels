from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings

from settings.base import COMMON_MODEL_CONFIG


class AuthSettings(BaseSettings):
    model_config = COMMON_MODEL_CONFIG

    jwt_secret: str = Field(min_length=8)
    jwt_algorithm: str
    access_token_ttl_minutes: int
    refresh_token_ttl_days: int
