from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

from settings.auth import AuthSettings
from settings.base import BASE_DIR, COMMON_MODEL_CONFIG
from settings.db import DBSettings


class AppSettings(BaseSettings):
    model_config = COMMON_MODEL_CONFIG

    app_name: str
    countries_geojson_path: Path
    auth: AuthSettings = Field(default_factory=AuthSettings)
    db: DBSettings = Field(default_factory=DBSettings)

    @property
    def resolved_countries_geojson_path(self) -> Path:
        if self.countries_geojson_path.is_absolute():
            return self.countries_geojson_path
        return BASE_DIR / self.countries_geojson_path


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()
