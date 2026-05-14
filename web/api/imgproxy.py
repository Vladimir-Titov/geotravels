import logging

from litestar import Request, Response, Router, get
from litestar.exceptions import HTTPException

logger = logging.getLogger(__name__)

_FORWARDED_RESPONSE_HEADERS = frozenset(
    {
        'cache-control',
        'etag',
        'expires',
        'last-modified',
    }
)


@get('/{proxy_path:path}', tags=['imgproxy'])
async def proxy_imgproxy_request(proxy_path: str, request: Request) -> Response[bytes]:
    settings = request.app.state.settings.imgproxy
    raw_path = request.scope.get('raw_path', b'').decode().split('?', maxsplit=1)[0]
    route_prefix = '/api/imgproxy/'
    upstream_path = raw_path.removeprefix(route_prefix) if raw_path.startswith(route_prefix) else proxy_path.lstrip('/')
    target_url = f'{settings.internal_base_url.rstrip("/")}/{upstream_path}'
    query_string = request.scope.get('query_string', b'').decode()
    if query_string:
        target_url = f'{target_url}?{query_string}'

    try:
        async with request.app.state.http_client_session.get(target_url) as upstream:
            content = await upstream.read()
            headers = {
                name: value
                for name, value in upstream.headers.items()
                if name.lower() in _FORWARDED_RESPONSE_HEADERS
            }
            return Response(
                content=content,
                status_code=upstream.status,
                media_type=upstream.headers.get('Content-Type', 'application/octet-stream'),
                headers=headers,
            )
    except Exception as exc:  # noqa: BLE001
        logger.exception('Imgproxy upstream request failed: %s', target_url)
        raise HTTPException(status_code=502, detail='Imgproxy upstream is unavailable') from exc


imgproxy_router = Router(path='/api/imgproxy', route_handlers=[proxy_imgproxy_request])
