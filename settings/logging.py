from __future__ import annotations

from pydantic_settings import BaseSettings

from settings.base import COMMON_MODEL_CONFIG


class LogSettings(BaseSettings):
    model_config = COMMON_MODEL_CONFIG

    log_level: str = 'INFO'
    # JSON-строка с уровнями для конкретных модулей.
    # Пример: GEOTRAVELS_LOG_MODULE_LEVELS='{"app.services": "DEBUG", "sqlalchemy.engine": "WARNING"}'
    log_module_levels: dict[str, str] = {}
