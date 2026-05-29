from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from settings.base import BASE_DIR


class DeepSeekSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            BASE_DIR / '.env.example',
            BASE_DIR / '.env',
        ),
        env_file_encoding='utf-8',
        env_prefix='GEOTRAVELS_DEEPSEEK_',
        extra='ignore',
    )

    base_url: str = 'https://api.deepseek.com/'
    api_key: str = ''
    timeout_seconds: float = Field(default=30.0, gt=0)
