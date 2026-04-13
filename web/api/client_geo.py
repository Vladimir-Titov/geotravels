from __future__ import annotations

from litestar import Router, get

from app.services.client_geo_search import ClientGeoSearchService
from app.services.current_user import CurrentUser
from web.api.schemas import (
    CitiesListRequest,
    CitiesListResponse,
    CityResponse,
    CountriesListRequest,
    CountriesListResponse,
    CountryResponse,
    PaginationResponse,
)
from web.utils import from_query


@get(
    '/countries',
    tags=['client-geo'],
    security=[{'user_auth': []}],
    dependencies={'filters': from_query(CountriesListRequest)},
)
async def list_client_countries(
    client_geo_search_service: ClientGeoSearchService,
    current_user: CurrentUser,  # noqa: ARG001
    filters: CountriesListRequest,
) -> CountriesListResponse:
    data = await client_geo_search_service.search_countries(**filters.to_repo_filters())
    return CountriesListResponse(
        items=[CountryResponse(**country) for country in data.items],
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
    dependencies={'filters': from_query(CitiesListRequest)},
)
async def list_client_cities(
    client_geo_search_service: ClientGeoSearchService,
    current_user: CurrentUser,  # noqa: ARG001
    filters: CitiesListRequest,
) -> CitiesListResponse:
    data = await client_geo_search_service.search_cities(**filters.to_repo_filters())
    return CitiesListResponse(
        items=[CityResponse(**city) for city in data.items],
        pagination=PaginationResponse(
            limit=data.pagination.limit,
            offset=data.pagination.offset,
            total=data.pagination.total,
        ),
    )


client_geo_router = Router(path='/api/v1/geo', route_handlers=[list_client_countries, list_client_cities])
