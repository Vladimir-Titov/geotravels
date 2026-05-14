from pathlib import Path

from litestar.testing import TestClient

from settings import AppSettings, AuthSettings, ClientGeoSettings, ImgproxySettings, LogSettings, OtpSettings
from web.app import create_app


class DummyFileStorage:
    def build_file_url(self, key: str) -> str:
        return f'memory://{key}'

    async def upload_file(self, key: str, content: bytes, file_type: str | None = None) -> str:  # noqa: ARG002
        return self.build_file_url(key)

    async def exists_file(self, file_url: str) -> bool:  # noqa: ARG002
        return False

    async def delete_file(self, file_url: str) -> None:  # noqa: ARG002
        return None

    async def download_file(self, file_url: str) -> bytes:  # noqa: ARG002
        return b''

    async def check_connection(self) -> bool:
        return True


class FakeImgproxyResponse:
    status = 200
    headers = {
        'Content-Type': 'image/webp',
        'Cache-Control': 'public, max-age=31536000',
    }

    async def __aenter__(self) -> 'FakeImgproxyResponse':
        return self

    async def __aexit__(self, *_args: object) -> None:
        return None

    async def read(self) -> bytes:
        return b'webp-bytes'


class FakeHttpSession:
    def __init__(self) -> None:
        self.requested_url: str | None = None

    def get(self, url: str) -> FakeImgproxyResponse:
        self.requested_url = url
        return FakeImgproxyResponse()


def _settings() -> AppSettings:
    return AppSettings(
        environment='test',
        countries_geojson_path=Path('data/countries.geojson'),
        auth=AuthSettings(jwt_secret='test-secret-123456789012345678901234', telegram_bot_token='test-token'),
        otp=OtpSettings(otp_mock_code='654321'),
        client_geo=ClientGeoSettings(geonames_username='demo'),
        imgproxy=ImgproxySettings(
            internal_base_url='http://imgproxy:8080',
            key='736563726574',
            salt='68656c6c6f',
        ),
        log=LogSettings(sentry_enable=False),
    )


def test_imgproxy_route_proxies_generated_urls_to_configured_upstream() -> None:
    http_session = FakeHttpSession()
    app = create_app(
        settings=_settings(),
        db_pool=object(),
        file_storage=DummyFileStorage(),
        http_session=http_session,
    )

    with TestClient(app=app) as client:
        response = client.get('/api/imgproxy/signature/plain/s3%3A%2F%2Fbucket%2Fpath%2Fphoto.webp@webp?cache=bust')

    assert response.status_code == 200
    assert response.content == b'webp-bytes'
    assert response.headers['content-type'] == 'image/webp'
    assert response.headers['cache-control'] == 'public, max-age=31536000'
    assert (
        http_session.requested_url
        == 'http://imgproxy:8080/signature/plain/s3%3A%2F%2Fbucket%2Fpath%2Fphoto.webp@webp?cache=bust'
    )
