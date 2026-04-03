from litestar import Router, get

from app.services.countries import CountriesService
from app.services.current_user import CurrentUser
from web.api.schemas import CountriesListRequest, CountriesListResponse, CountryResponse, PaginationResponse
from web.utils import from_query


@get(
    '',
    tags=['countries'],
    security=[{'user_auth': []}],
    dependencies={'filters': from_query(CountriesListRequest)},
)
async def list_countries(
    countries_service: CountriesService,
    current_user: CurrentUser,  # noqa: ARG001
    filters: CountriesListRequest,
) -> CountriesListResponse:
    data = await countries_service.list_countries(**filters.to_repo_filters())
    return CountriesListResponse(
        items=[CountryResponse(**country) for country in data.items],
        pagination=PaginationResponse(
            limit=data.pagination.limit,
            offset=data.pagination.offset,
            total=data.pagination.total,
        ),
    )


countries_router = Router(path='/api/v1/countries', route_handlers=[list_countries])
