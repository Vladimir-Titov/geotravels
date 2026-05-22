from uuid import UUID

from litestar import Router, get

from app.services.client_geo_search import ClientGeoSearchService
from app.services.current_user import CurrentUser
from app.services.places import PlacesService
from web.api.client_geo.schemas import (
    ClientGeoCitiesListRequest,
    ClientGeoCitiesListResponse,
    ClientGeoCityResponse,
    ClientGeoCountriesListRequest,
    ClientGeoCountriesListResponse,
    ClientGeoCountryResponse,
    PaginationResponse,
)
from web.utils import from_query


@get(
    '/countries',
    tags=['client-geo'],
    security=[{'user_auth': []}],
    dependencies={'filters': from_query(ClientGeoCountriesListRequest)},
)
async def list_client_countries(
    client_geo_search_service: ClientGeoSearchService,
    current_user: CurrentUser,  # noqa: ARG001
    filters: ClientGeoCountriesListRequest,
) -> ClientGeoCountriesListResponse:
    data = await client_geo_search_service.search_countries(lang=filters.normalized_lang, **filters.to_repo_filters())
    return ClientGeoCountriesListResponse(
        items=[ClientGeoCountryResponse(**country) for country in data.items],
        pagination=PaginationResponse(
            limit=data.pagination.limit,
            offset=data.pagination.offset,
            total=data.pagination.total,
        ),
    )


@get(
    '/cities',
    tags=['client-geo'],
    security=[{'user_auth': []}],
    dependencies={'filters': from_query(ClientGeoCitiesListRequest)},
)
async def list_client_cities(
    client_geo_search_service: ClientGeoSearchService,
    current_user: CurrentUser,  # noqa: ARG001
    filters: ClientGeoCitiesListRequest,
) -> ClientGeoCitiesListResponse:
    data = await client_geo_search_service.search_cities(lang=filters.normalized_lang, **filters.to_repo_filters())
    return ClientGeoCitiesListResponse(
        items=[ClientGeoCityResponse(**city) for city in data.items],
        pagination=PaginationResponse(
            limit=data.pagination.limit,
            offset=data.pagination.offset,
            total=data.pagination.total,
        ),
    )


@get('/cities/{city_id:uuid}/places', tags=['client-geo'], security=[{'user_auth': []}])
async def suggest_client_city_places(
    city_id: UUID,
    places_service: PlacesService,
    current_user: CurrentUser,  # noqa: ARG001
) -> list[str]:
    return await places_service.suggest_places(city_id=city_id)


client_geo_router = Router(
    path='/api/v1/geo',
    route_handlers=[
        list_client_countries,
        list_client_cities,
        suggest_client_city_places,
    ],
)
