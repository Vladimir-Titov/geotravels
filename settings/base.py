from pathlib import Path

from pydantic_settings import SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

COMMON_MODEL_CONFIG = SettingsConfigDict(
    env_file=(
        BASE_DIR / '.env.example',
        BASE_DIR / '.env',
    ),
    env_file_encoding='utf-8',
    env_prefix='GEOTRAVELS_',
    extra='ignore',
)
