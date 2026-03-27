from litestar import MediaType, Router, get
from litestar.response import Response

from app.services.countries import CountriesService
from web.api.schemas import CountriesListResponse, CountryResponse


@get('', tags=['countries'])
async def list_countries(countries_service: CountriesService) -> CountriesListResponse:
    countries = await countries_service.list_countries()
    return CountriesListResponse(items=[CountryResponse(**country) for country in countries])


@get('/geojson', tags=['countries'], media_type=MediaType.JSON)
async def countries_geojson(countries_service: CountriesService) -> Response[bytes]:
    path = countries_service.settings.resolved_countries_geojson_path
    return Response(content=path.read_bytes(), media_type=MediaType.JSON)


countries_router = Router(path='/api/v1/countries', route_handlers=[list_countries, countries_geojson])
