import pytest
from litestar.datastructures import UploadFile
from pydantic import ValidationError

from web.api.schemas import UploadFileRequest


def _upload_file(content_type: str) -> UploadFile:
    return UploadFile(content_type=content_type, filename='photo.jpg', file_data=b'image-bytes')


@pytest.mark.parametrize(
    'content_type',
    [
        'image/jpeg',
        'image/jpg',
        'image/png',
        'image/webp',
        'image/heic',
        'image/heif',
        'image/heic-sequence',
        'image/heif-sequence',
        'image/x-heic',
        'image/x-heif',
        'IMAGE/JPEG; charset=binary',
    ],
)
def test_upload_file_request_accepts_supported_image_content_types(content_type: str) -> None:
    request = UploadFileRequest(file=_upload_file(content_type))

    assert request.file.content_type == content_type


@pytest.mark.parametrize('content_type', ['application/pdf', 'application/octet-stream', 'text/plain', ''])
def test_upload_file_request_rejects_unsupported_content_types(content_type: str) -> None:
    with pytest.raises(ValidationError, match='file content type must be one of'):
        UploadFileRequest(file=_upload_file(content_type))
