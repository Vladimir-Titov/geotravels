from __future__ import annotations

from typing import Any

from litestar import Router, get

from app.services.countries import CountriesService
from web.api.schemas import CountriesListResponse, CountryResponse


@get('', tags=['countries'])
async def list_countries(countries_service: CountriesService) -> CountriesListResponse:
    countries = await countries_service.list_countries()
    return CountriesListResponse(items=[CountryResponse(**country) for country in countries])


@get('/geojson', tags=['countries'])
async def countries_geojson(countries_service: CountriesService) -> dict[str, Any]:
    return countries_service.get_geojson()


countries_router = Router(path='/api/v1/countries', route_handlers=[list_countries, countries_geojson])
