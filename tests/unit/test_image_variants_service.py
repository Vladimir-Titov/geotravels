from uuid import uuid4

import pytest

from app.services.image_variants import ImageTransformer, ImageVariant, ImageVariantService


class MemoryFileStorage:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self.downloads: dict[str, int] = {}
        self.uploads: dict[str, int] = {}

    def build_file_url(self, key: str) -> str:
        return f'memory://{key}'

    async def upload_file(self, key: str, content: bytes, file_type: str | None = None) -> str:  # noqa: ARG002
        self.objects[key] = content
        self.uploads[key] = self.uploads.get(key, 0) + 1
        return self.build_file_url(key)

    async def exists_file(self, file_url: str) -> bool:
        key = file_url.removeprefix('memory://')
        return key in self.objects

    async def delete_file(self, file_url: str) -> None:
        key = file_url.removeprefix('memory://')
        self.objects.pop(key, None)

    async def download_file(self, file_url: str) -> bytes:
        key = file_url.removeprefix('memory://')
        self.downloads[key] = self.downloads.get(key, 0) + 1
        return self.objects[key]

    async def check_connection(self) -> bool:
        return True


def _sample_image(width: int = 1200, height: int = 800) -> bytes:
    import pyvips

    return pyvips.Image.black(width, height).new_from_image(255).write_to_buffer('.png')


def _image_size(content: bytes) -> tuple[int, int]:
    import pyvips

    image = pyvips.Image.new_from_buffer(content, '')
    return image.width, image.height


def test_image_transformer_resizes_without_upscaling() -> None:
    transformer = ImageTransformer()

    resized = transformer.resize_to_webp(_sample_image(width=1200, height=800), max_side=480, quality=72)
    assert _image_size(resized) == (480, 320)

    small = transformer.resize_to_webp(_sample_image(width=120, height=80), max_side=480, quality=72)
    assert _image_size(small) == (120, 80)


@pytest.mark.asyncio
async def test_image_variant_service_generates_missing_variant_once() -> None:
    file_id = uuid4()
    storage = MemoryFileStorage()
    full_url = await storage.upload_file('uploads/photo.webp', _sample_image(), 'image/webp')
    service = ImageVariantService(file_storage=storage, transformer=ImageTransformer())

    first = await service.get_variant(file_id=file_id, file_url=full_url, variant=ImageVariant.THUMB)
    second = await service.get_variant(file_id=file_id, file_url=full_url, variant=ImageVariant.THUMB)

    variant_key = f'variants/{file_id}/thumb.webp'
    assert variant_key in storage.objects
    assert storage.uploads[variant_key] == 1
    assert storage.downloads['uploads/photo.webp'] == 1
    assert storage.downloads[variant_key] == 1
    assert first.content_type == 'image/webp'
    assert second.content == storage.objects[variant_key]


@pytest.mark.asyncio
async def test_image_variant_service_uses_existing_variant_without_reading_full_file() -> None:
    file_id = uuid4()
    storage = MemoryFileStorage()
    full_url = await storage.upload_file('uploads/photo.webp', _sample_image(), 'image/webp')
    variant_content = ImageTransformer().resize_to_webp(_sample_image(), max_side=480, quality=72)
    await storage.upload_file(f'variants/{file_id}/thumb.webp', variant_content, 'image/webp')
    storage.downloads.clear()
    service = ImageVariantService(file_storage=storage, transformer=ImageTransformer())

    result = await service.get_variant(file_id=file_id, file_url=full_url, variant=ImageVariant.THUMB)

    assert result.content == variant_content
    assert storage.downloads == {f'variants/{file_id}/thumb.webp': 1}
