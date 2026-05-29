from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest

from app.repositories.base import RowNotFoundError
from app.services.exceptions import NotFoundError, ServiceError
from app.services.geoapify.schemas import GeoApifyPlaceResponse
from app.services.places import PlacesService


class FakeCitiesRepository:
    def __init__(self, city: dict | None = None, exc: Exception | None = None) -> None:
        self.city = city or {}
        self.exc = exc
        self.city_ids: list[UUID] = []

    async def get_by_id(self, city_id: UUID) -> dict:
        self.city_ids.append(city_id)
        if self.exc is not None:
            raise self.exc
        return self.city


class FakeGeoApifyClient:
    def __init__(self, response: GeoApifyPlaceResponse) -> None:
        self.response = response
        self.requests = []

    async def search_places(self, request):
        self.requests.append(request)
        return self.response


class FakeDeepSeekClient:
    def __init__(
        self,
        response_text: str = '[{"place":"Medeu","desc":"Mountain rink.","address":"Medeu"}]',
    ) -> None:
        self.response_text = response_text
        self.requests = []

    async def completions(self, request):
        self.requests.append(request)
        return SimpleNamespace(choices=(SimpleNamespace(text=self.response_text),))


def _places_response() -> GeoApifyPlaceResponse:
    return GeoApifyPlaceResponse.from_dict(
        {
            'features': [
                {
                    'properties': {
                        'name': ' Medeu ',
                        'formatted': 'Medeu, Almaty, Kazakhstan',
                        'categories': ['heritage.unesco'],
                        'wiki_and_media': {'wikidata': 'Q999'},
                    },
                    'geometry': {'type': 'Point', 'coordinates': [77.0589, 43.1571]},
                },
                {
                    'properties': {'name': 'medeu', 'categories': ['leisure.park']},
                    'geometry': {'type': 'Point', 'coordinates': [77.0589, 43.1571]},
                },
                {
                    'properties': {
                        'name': 'Kok Tobe',
                        'formatted': '',
                        'address_line2': 'Kok Tobe hill, Almaty, Kazakhstan',
                        'categories': ['tourism.attraction'],
                    },
                    'geometry': {'type': 'Point', 'coordinates': [76.9754, 43.2345]},
                },
                {
                    'properties': {},
                    'geometry': {'type': 'Point', 'coordinates': [76.9, 43.2]},
                },
            ],
        }
    )


@pytest.mark.asyncio
async def test_suggest_places_uses_city_meta_coordinates_and_passes_deduplicated_addresses_to_prompt() -> None:
    city_id = uuid4()
    city = {
        'id': city_id,
        'name': 'Almaty',
        'country_code': 'KZ',
        'meta': {
            'lat': '43.25249',
            'lng': '76.9115',
            'bbox': {
                'west': 76.66018110287332,
                'south': 43.06999292215793,
                'east': 77.16281689712669,
                'north': 43.434984397842065,
            },
        },
    }
    geoapify_client = FakeGeoApifyClient(_places_response())
    deepseek_client = FakeDeepSeekClient()
    service = PlacesService(
        geoapify_client=geoapify_client,
        cities_repository=FakeCitiesRepository(city),
        deepseek_client=deepseek_client,
    )

    places = await service.suggest_places(city_id)

    request = geoapify_client.requests[0]
    assert places == [{'place': 'Medeu', 'desc': 'Mountain rink.', 'address': 'Medeu'}]
    assert "{'Medeu': 'Medeu, Almaty, Kazakhstan'}" in deepseek_client.requests[0].prompt
    assert "{'Kok Tobe': 'Kok Tobe hill, Almaty, Kazakhstan'}" in deepseek_client.requests[0].prompt
    assert request.to_query_params() == {
        'categories': (
            'tourism.attraction,tourism.attraction.viewpoint,tourism.sights,entertainment.museum,'
            'heritage,heritage.unesco,national_park,leisure.park,leisure.park.garden,'
            'leisure.park.nature_reserve,natural.protected_area'
        ),
        'conditions': 'named',
        'filter': 'circle:76.9115,43.25249,50000',
        'bias': 'proximity:76.9115,43.25249',
        'limit': 100,
        'lang': 'en',
    }


@pytest.mark.asyncio
async def test_suggest_places_passes_normalized_lang_to_geoapify() -> None:
    geoapify_client = FakeGeoApifyClient(GeoApifyPlaceResponse(features=()))
    service = PlacesService(
        geoapify_client=geoapify_client,
        cities_repository=FakeCitiesRepository(
            {'name': 'Almaty', 'country_code': 'KZ', 'meta': {'lat': '43.25249', 'lng': '76.9115'}}
        ),
        deepseek_client=FakeDeepSeekClient(),
    )

    await service.suggest_places(uuid4(), lang='ru-RU')

    assert geoapify_client.requests[0].to_query_params()['lang'] == 'ru'


@pytest.mark.asyncio
async def test_suggest_places_uses_localized_place_name_when_available() -> None:
    response = GeoApifyPlaceResponse.from_dict(
        {
            'features': [
                {
                    'properties': {
                        'name': 'Музей изобразительных искусств',
                        'name_international': {
                            'en': 'Museum of fine arts',
                            'ru': 'Музей изобразительных искусств',
                        },
                        'address_line3': 'Museum street, 1, Russia',
                        'categories': ['entertainment.museum'],
                    },
                    'geometry': {'type': 'Point', 'coordinates': [31.27104, 58.52131]},
                },
                {
                    'properties': {
                        'name': 'Важня',
                        'categories': ['heritage'],
                    },
                    'geometry': {'type': 'Point', 'coordinates': [31.27104, 58.52131]},
                },
            ],
        }
    )
    geoapify_client = FakeGeoApifyClient(response)
    deepseek_client = FakeDeepSeekClient()
    service = PlacesService(
        geoapify_client=geoapify_client,
        cities_repository=FakeCitiesRepository(
            {'name': 'Veliky Novgorod', 'country_code': 'RU', 'meta': {'lat': '58.52131', 'lng': '31.27104'}}
        ),
        deepseek_client=deepseek_client,
    )

    await service.suggest_places(uuid4(), lang='en')

    assert "{'Museum of fine arts': 'Museum street, 1, Russia'}" in deepseek_client.requests[0].prompt
    assert "{'Важня': ''}" in deepseek_client.requests[0].prompt


@pytest.mark.asyncio
async def test_suggest_places_falls_back_to_default_lang() -> None:
    geoapify_client = FakeGeoApifyClient(GeoApifyPlaceResponse(features=()))
    service = PlacesService(
        geoapify_client=geoapify_client,
        cities_repository=FakeCitiesRepository(
            {'name': 'Almaty', 'country_code': 'KZ', 'meta': {'lat': '43.25249', 'lng': '76.9115'}}
        ),
        deepseek_client=FakeDeepSeekClient(),
    )

    await service.suggest_places(uuid4(), lang='invalid')

    assert geoapify_client.requests[0].to_query_params()['lang'] == 'en'


@pytest.mark.asyncio
async def test_suggest_places_falls_back_to_circle_filter() -> None:
    geoapify_client = FakeGeoApifyClient(GeoApifyPlaceResponse(features=()))
    service = PlacesService(
        geoapify_client=geoapify_client,
        cities_repository=FakeCitiesRepository(
            {'name': 'Almaty', 'country_code': 'KZ', 'meta': {'lat': '43.25249', 'lng': '76.9115'}}
        ),
        deepseek_client=FakeDeepSeekClient(),
    )

    await service.suggest_places(uuid4())

    assert geoapify_client.requests[0].to_query_params()['filter'] == 'circle:76.9115,43.25249,50000'


@pytest.mark.asyncio
async def test_suggest_places_uses_city_bbox_to_expand_radius_for_large_city() -> None:
    geoapify_client = FakeGeoApifyClient(GeoApifyPlaceResponse(features=()))
    service = PlacesService(
        geoapify_client=geoapify_client,
        deepseek_client=FakeDeepSeekClient(),
        cities_repository=FakeCitiesRepository(
            {
                'name': 'Almaty',
                'country_code': 'KZ',
                'meta': {
                    'lat': '43.25249',
                    'lng': '76.9115',
                    'bbox': {
                        'west': 75.0,
                        'south': 42.0,
                        'east': 78.0,
                        'north': 44.0,
                    },
                }
            }
        ),
    )

    await service.suggest_places(uuid4())

    query_params = geoapify_client.requests[0].to_query_params()
    assert query_params['filter'].startswith('circle:76.9115,43.25249,')
    assert int(str(query_params['filter']).rsplit(',', maxsplit=1)[1]) > 50_000


@pytest.mark.asyncio
async def test_suggest_places_raises_not_found_for_missing_city() -> None:
    service = PlacesService(
        geoapify_client=FakeGeoApifyClient(GeoApifyPlaceResponse(features=())),
        cities_repository=FakeCitiesRepository(exc=RowNotFoundError()),
        deepseek_client=FakeDeepSeekClient(),
    )

    with pytest.raises(NotFoundError):
        await service.suggest_places(uuid4())


@pytest.mark.asyncio
async def test_suggest_places_requires_city_coordinates() -> None:
    service = PlacesService(
        geoapify_client=FakeGeoApifyClient(GeoApifyPlaceResponse(features=())),
        cities_repository=FakeCitiesRepository({'meta': {}}),
        deepseek_client=FakeDeepSeekClient(),
    )

    with pytest.raises(ServiceError, match='City coordinates not found'):
        await service.suggest_places(uuid4())
