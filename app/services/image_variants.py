import base64
import hashlib
import hmac
from dataclasses import dataclass
from enum import StrEnum
from urllib.parse import quote

from settings import ImgproxySettings


class ImageVariant(StrEnum):
    FULL = 'full'
    PREVIEW = 'preview'
    THUMB = 'thumb'


@dataclass(frozen=True)
class ImageVariantSpec:
    max_side: int
    quality: int


IMAGE_VARIANT_SPECS: dict[ImageVariant, ImageVariantSpec] = {
    ImageVariant.FULL: ImageVariantSpec(max_side=1600, quality=80),
    ImageVariant.PREVIEW: ImageVariantSpec(max_side=1280, quality=84),
    ImageVariant.THUMB: ImageVariantSpec(max_side=720, quality=82),
}


class ImageVariantService:
    def __init__(self, settings: ImgproxySettings):
        self.settings = settings

    @staticmethod
    def _decode_hex_secret(value: str, name: str) -> bytes:
        try:
            return bytes.fromhex(value)
        except ValueError as exc:
            raise ValueError(f'{name} must be hex-encoded') from exc

    def _sign_path(self, path: str) -> str:
        key = self._decode_hex_secret(self.settings.key, 'IMGPROXY_KEY')
        salt = self._decode_hex_secret(self.settings.salt, 'IMGPROXY_SALT')
        digest = hmac.new(key, salt + path.encode(), hashlib.sha256).digest()
        return base64.urlsafe_b64encode(digest).rstrip(b'=').decode()

    @staticmethod
    def _source_url(file_url: str) -> str:
        return quote(file_url, safe='')

    def get_variant_url(self, file_url: str | None, variant: ImageVariant = ImageVariant.FULL) -> str | None:
        if file_url is None:
            return None

        spec = IMAGE_VARIANT_SPECS[variant]
        path = f'/rs:fit:{spec.max_side}:{spec.max_side}:0/q:{spec.quality}/plain/{self._source_url(file_url)}@webp'
        signature = self._sign_path(path)
        return f'{self.settings.base_url.rstrip("/")}/{signature}{path}'
