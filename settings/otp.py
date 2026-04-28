from pydantic_settings import BaseSettings

from settings.base import COMMON_MODEL_CONFIG


class OtpSettings(BaseSettings):
    model_config = COMMON_MODEL_CONFIG

    otp_ttl_minutes: int = 10
    otp_max_attempts: int = 5
    otp_rate_limit_seconds: int = 60
    otp_mock_code: str | None = None

    resend_api_key: str = ''
    resend_email_from: str = 'TripMark <noreply@tripmark.ru>'
