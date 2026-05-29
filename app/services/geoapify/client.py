import logging
from typing import Any
from urllib.parse import urljoin

from aiohttp import ClientSession

from app.services.geoapify.schemas import GeoApifyPlaceRequest, GeoApifyPlaceResponse
from settings import GeoApifySettings

logger = logging.getLogger(__name__)


class GeoApifyClient:
    def __init__(self, settings: GeoApifySettings, session: ClientSession):
        self.settings = settings
        self.base_url = settings.base_url.rstrip('/')
        self.session = session

    async def search_places(self, request: GeoApifyPlaceRequest | dict[str, Any]) -> GeoApifyPlaceResponse:
        try:
            payload = await self._request_places(self.session, params=self._build_params(request))
            return GeoApifyPlaceResponse.from_dict(payload)
        except Exception as exc:  # noqa: BLE001
            logger.warning('Geoapify places request failed: %s', exc)
            return GeoApifyPlaceResponse(features=())

    async def _request_places(self, session: ClientSession, *, params: dict[str, Any]) -> dict[str, Any]:
        url = urljoin(self.base_url, '/v2/places')
        async with session.get(
            url,
            params=params,
            timeout=self.settings.timeout_seconds,
        ) as response:
            response.raise_for_status()
            payload = await response.json()

        return payload if isinstance(payload, dict) else {}

    def _build_params(self, request: GeoApifyPlaceRequest | dict[str, Any]) -> dict[str, Any]:
        if isinstance(request, GeoApifyPlaceRequest):
            return request.to_query_params(api_key=self.settings.api_key)

        return {'apiKey': self.settings.api_key, **request}
