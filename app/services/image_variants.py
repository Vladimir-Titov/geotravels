import asyncio
import hashlib
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

import pyvips

from app.services.file_storage import FileStorage
from helpers import InvalidImageError


class ImageVariant(StrEnum):
    FULL = 'full'
    PREVIEW = 'preview'
    THUMB = 'thumb'


@dataclass(frozen=True)
class ImageVariantSpec:
    max_side: int | None
    quality: int


@dataclass(frozen=True)
class ImageVariantData:
    content: bytes
    content_type: str
    etag: str
    variant: ImageVariant


IMAGE_VARIANT_SPECS: dict[ImageVariant, ImageVariantSpec] = {
    ImageVariant.FULL: ImageVariantSpec(max_side=None, quality=80),
    ImageVariant.PREVIEW: ImageVariantSpec(max_side=960, quality=78),
    ImageVariant.THUMB: ImageVariantSpec(max_side=480, quality=72),
}


class ImageTransformer:
    def resize_to_webp(self, raw_image: bytes, max_side: int, quality: int) -> bytes:
        try:
            image = pyvips.Image.new_from_buffer(raw_image, '', access='sequential')
            image = image.autorot()

            largest_side = max(image.width, image.height)
            if largest_side > max_side:
                image = image.resize(max_side / largest_side)

            return image.write_to_buffer('.webp', Q=quality, strip=True)
        except pyvips.Error as exc:
            raise InvalidImageError from exc


class ImageVariantService:
    def __init__(self, file_storage: FileStorage, transformer: ImageTransformer):
        self.file_storage = file_storage
        self.transformer = transformer
        self._locks: dict[str, asyncio.Lock] = {}
        self._lock_ref_counts: dict[str, int] = {}
        self._locks_guard = asyncio.Lock()

    def _variant_url(self, file_id: UUID, variant: ImageVariant) -> str:
        return self.file_storage.build_file_url(f'variants/{file_id}/{variant.value}.webp')

    @staticmethod
    def _etag(content: bytes, variant: ImageVariant) -> str:
        digest = hashlib.sha256(content).hexdigest()
        return f'"{variant.value}-{digest}"'

    def get_variant_download_url(self, file_id: UUID, variant: ImageVariant) -> str:
        if variant == ImageVariant.FULL:
            return f'/api/v1/files/{file_id}/download'
        return f'/api/v1/files/{file_id}/download?variant={variant.value}'

    async def _run_with_variant_lock(
        self,
        lock_key: str,
        action: Callable[[], Awaitable[ImageVariantData]],
    ) -> ImageVariantData:
        async with self._locks_guard:
            lock = self._locks.setdefault(lock_key, asyncio.Lock())
            self._lock_ref_counts[lock_key] = self._lock_ref_counts.get(lock_key, 0) + 1

        await lock.acquire()
        try:
            return await action()
        finally:
            lock.release()
            async with self._locks_guard:
                remaining = self._lock_ref_counts.get(lock_key, 1) - 1
                if remaining <= 0:
                    self._lock_ref_counts.pop(lock_key, None)
                    self._locks.pop(lock_key, None)
                else:
                    self._lock_ref_counts[lock_key] = remaining

    async def get_variant(self, file_id: UUID, file_url: str, variant: ImageVariant) -> ImageVariantData:
        if variant == ImageVariant.FULL:
            content = await self.file_storage.download_file(file_url)
            return ImageVariantData(
                content=content,
                content_type='image/webp',
                etag=self._etag(content, variant),
                variant=variant,
            )

        variant_url = self._variant_url(file_id=file_id, variant=variant)
        lock_key = f'{file_id}:{variant.value}'

        async def load_or_generate_variant() -> ImageVariantData:
            if await self.file_storage.exists_file(variant_url):
                content = await self.file_storage.download_file(variant_url)
                return ImageVariantData(
                    content=content,
                    content_type='image/webp',
                    etag=self._etag(content, variant),
                    variant=variant,
                )

            source = await self.file_storage.download_file(file_url)
            spec = IMAGE_VARIANT_SPECS[variant]
            if spec.max_side is None:
                content = source
            else:
                content = await asyncio.to_thread(
                    self.transformer.resize_to_webp,
                    raw_image=source,
                    max_side=spec.max_side,
                    quality=spec.quality,
                )

            await self.file_storage.upload_file(
                key=f'variants/{file_id}/{variant.value}.webp',
                content=content,
                file_type='image/webp',
            )
            return ImageVariantData(
                content=content,
                content_type='image/webp',
                etag=self._etag(content, variant),
                variant=variant,
            )

        return await self._run_with_variant_lock(lock_key, load_or_generate_variant)

    async def delete_variants(self, file_id: UUID) -> None:
        for variant in (ImageVariant.PREVIEW, ImageVariant.THUMB):
            variant_url = self._variant_url(file_id=file_id, variant=variant)
            if await self.file_storage.exists_file(variant_url):
                await self.file_storage.delete_file(variant_url)
