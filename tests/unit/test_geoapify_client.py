import pytest

from app.services.geoapify.categories import GeoApifyPlaceCategory
from app.services.geoapify.client import GeoApifyClient
from app.services.geoapify.schemas import (
    GeoApifyPlaceCircleFilter,
    GeoApifyPlaceProximityBias,
    GeoApifyPlaceRequest,
)
from settings import GeoApifySettings


class FakeGeoApifyResponse:
    def __init__(self, payload: dict | None = None, exc: Exception | None = None) -> None:
        self.payload = payload or {}
        self.exc = exc

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        return None

    def raise_for_status(self) -> None:
        if self.exc is not None:
            raise self.exc

    async def json(self) -> dict:
        return self.payload


class FakeGeoApifySession:
    def __init__(self, response: FakeGeoApifyResponse) -> None:
        self.response = response
        self.calls: list[dict] = []

    def get(self, url: str, *, params: dict, timeout: float) -> FakeGeoApifyResponse:
        self.calls.append({'url': url, 'params': params, 'timeout': timeout})
        return self.response


def _settings() -> GeoApifySettings:
    return GeoApifySettings(
        base_url='https://geoapify.example.test/',
        api_key='test-api-key',
        timeout_seconds=2.5,
    )


@pytest.mark.asyncio
async def test_places_sends_geoapify_request_and_parses_feature_collection() -> None:
    session = FakeGeoApifySession(
        FakeGeoApifyResponse(
            {
                'type': 'FeatureCollection',
                'features': [
                    {
                        'type': 'Feature',
                        'properties': {
                            'name': 'Tower Bridge',
                            'country': 'United Kingdom',
                            'lat': 51.5055,
                            'lon': -0.0754,
                            'categories': ['tourism.sights'],
                            'place_id': 'place-id',
                        },
                        'geometry': {
                            'type': 'Point',
                            'coordinates': [-0.0754, 51.5055],
                        },
                    }
                ],
            }
        )
    )
    client = GeoApifyClient(_settings(), session=session)

    response = await client.search_places(
        GeoApifyPlaceRequest(
            categories=('tourism.sights',),
            filter=GeoApifyPlaceCircleFilter(lon=-0.07, lat=51.5, radius_meters=1000),
            bias=GeoApifyPlaceProximityBias(lon=-0.0754, lat=51.5055),
            limit=10,
            lang='en',
            name='tower',
        )
    )

    assert session.calls == [
        {
            'url': 'https://geoapify.example.test/v2/places',
            'params': {
                'categories': 'tourism.sights',
                'filter': 'circle:-0.07,51.5,1000',
                'bias': 'proximity:-0.0754,51.5055',
                'limit': 10,
                'lang': 'en',
                'name': 'tower',
                'apiKey': 'test-api-key',
            },
            'timeout': 2.5,
        }
    ]
    assert len(response) == 1
    assert response.features[0].properties.name == 'Tower Bridge'
    assert response.features[0].geometry.coordinates == (-0.0754, 51.5055)


@pytest.mark.asyncio
async def test_places_accepts_raw_params() -> None:
    session = FakeGeoApifySession(FakeGeoApifyResponse({'type': 'FeatureCollection', 'features': []}))
    client = GeoApifyClient(_settings(), session=session)

    response = await client.search_places({'categories': 'catering.restaurant', 'limit': 5})

    assert len(response) == 0
    assert session.calls[0]['params'] == {
        'apiKey': 'test-api-key',
        'categories': 'catering.restaurant',
        'limit': 5,
    }


def test_place_category_enum_keeps_geoapify_value_and_description() -> None:
    assert GeoApifyPlaceCategory.TOURISM_SIGHTS == 'tourism.sights'
    assert GeoApifyPlaceCategory.ACCOMMODATION.description == 'Place to stay or live'
    assert GeoApifyPlaceCategory.TOURISM_SIGHTS.description == ''

    request = GeoApifyPlaceRequest(categories=(GeoApifyPlaceCategory.TOURISM_SIGHTS,))

    assert request.to_query_params() == {'categories': 'tourism.sights'}


@pytest.mark.asyncio
async def test_places_returns_empty_response_on_request_failure() -> None:
    session = FakeGeoApifySession(FakeGeoApifyResponse(exc=RuntimeError('request failed')))
    client = GeoApifyClient(_settings(), session=session)

    response = await client.search_places({'categories': 'tourism.sights'})

    assert len(response) == 0
