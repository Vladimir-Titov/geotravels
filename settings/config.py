from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

from settings.auth import AuthSettings
from settings.base import BASE_DIR, COMMON_MODEL_CONFIG
from settings.db import DBSettings
from settings.logging import LogSettings


class AppSettings(BaseSettings):
    model_config = COMMON_MODEL_CONFIG

    app_name: str
    countries_geojson_path: Path
    cors_allowed_origins: str
    auth: AuthSettings = Field(default_factory=AuthSettings)
    db: DBSettings = Field(default_factory=DBSettings)
    log: LogSettings = Field(default_factory=LogSettings)

    @property
    def resolved_countries_geojson_path(self) -> Path:
        if self.countries_geojson_path.is_absolute():
            return self.countries_geojson_path
        return BASE_DIR / self.countries_geojson_path

    @property
    def resolved_cors_allowed_origins(self) -> list[str]:
        raw = self.cors_allowed_origins.strip()
        if not raw:
            return []

        if raw.startswith('['):
            parsed = json.loads(raw)
            if not isinstance(parsed, list):
                raise ValueError('GEOTRAVELS_CORS_ALLOWED_ORIGINS JSON value must be a list')
            return [str(item).strip() for item in parsed if str(item).strip()]

        return [item.strip() for item in raw.split(',') if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()
