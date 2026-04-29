from pydantic_settings import BaseSettings

from settings.base import COMMON_MODEL_CONFIG


class LogSettings(BaseSettings):
    model_config = COMMON_MODEL_CONFIG

    log_level: str = 'INFO'
    # JSON-строка с уровнями для конкретных модулей.
    # Пример: GEOTRAVELS_LOG_MODULE_LEVELS='{"app.services": "DEBUG", "sqlalchemy.engine": "WARNING"}'
    log_module_levels: dict[str, str] = {}
    sentry_enable: bool = False
    sentry_dsn: str | None = None
    sentry_traces_sample_rate: float = 1.0
    sentry_send_default_pii: bool = False
    sentry_attach_stacktrace: bool = False
