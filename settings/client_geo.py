from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings

from settings.base import COMMON_MODEL_CONFIG


class ClientGeoSettings(BaseSettings):
    model_config = COMMON_MODEL_CONFIG

    geonames_username: str | None = None
    geonames_base_url: str = 'https://api.geonames.org'
    geonames_timeout_seconds: float = Field(default=5.0, gt=0)
