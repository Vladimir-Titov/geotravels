import pytest

from app.services.image_variants import ImageVariant, ImageVariantService
from settings import ImgproxySettings


def _service() -> ImageVariantService:
    return ImageVariantService(
        ImgproxySettings(
            base_url='/api/imgproxy',
            key='736563726574',
            salt='68656c6c6f',
        )
    )


def test_image_variant_service_builds_signed_full_url() -> None:
    assert _service().get_variant_url(
        's3://user-bucket/uploads/photo.webp',
        ImageVariant.FULL,
    ) == (
        '/api/imgproxy/PqOTKu3wIxgOwmBZdP-iS3vr5yllU-smyrkzEaLZQtY'
        '/rs:fit:1600:1600:0/q:80/plain/s3%3A%2F%2Fuser-bucket%2Fuploads%2Fphoto.webp@webp'
    )


@pytest.mark.parametrize(
    ('variant', 'options'),
    [
        (ImageVariant.PREVIEW, '/rs:fit:960:960:0/q:78/'),
        (ImageVariant.THUMB, '/rs:fit:480:480:0/q:72/'),
    ],
)
def test_image_variant_service_uses_variant_options(variant: ImageVariant, options: str) -> None:
    url = _service().get_variant_url('s3://user-bucket/uploads/photo.webp', variant)

    assert url is not None
    assert url.startswith('/api/imgproxy/')
    assert options in url
    assert url.endswith('/plain/s3%3A%2F%2Fuser-bucket%2Fuploads%2Fphoto.webp@webp')


def test_image_variant_service_escapes_plain_source_url() -> None:
    url = _service().get_variant_url('s3://user-bucket/uploads/photo 100%.webp?x=@', ImageVariant.THUMB)

    assert url is not None
    assert url.endswith('/plain/s3%3A%2F%2Fuser-bucket%2Fuploads%2Fphoto%20100%25.webp%3Fx%3D%40@webp')


def test_image_variant_service_rejects_non_hex_secrets() -> None:
    service = ImageVariantService(ImgproxySettings(key='not-hex', salt='68656c6c6f'))

    with pytest.raises(ValueError, match='IMGPROXY_KEY must be hex-encoded'):
        service.get_variant_url('s3://user-bucket/uploads/photo.webp')
