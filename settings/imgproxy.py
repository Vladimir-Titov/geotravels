from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings

from settings.base import COMMON_MODEL_CONFIG


class ImgproxySettings(BaseSettings):
    model_config = COMMON_MODEL_CONFIG | {'populate_by_name': True}

    base_url: str = Field(
        default='http://localhost:8080',
        validation_alias='GEOTRAVELS_IMGPROXY_BASE_URL',
    )
    key: str = Field(
        default='736563726574',
        validation_alias=AliasChoices('GEOTRAVELS_IMGPROXY_KEY', 'IMGPROXY_KEY'),
    )
    salt: str = Field(
        default='68656c6c6f',
        validation_alias=AliasChoices('GEOTRAVELS_IMGPROXY_SALT', 'IMGPROXY_SALT'),
    )
