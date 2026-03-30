from uuid import UUID

from litestar import Router, delete, get, patch, post
from litestar.exceptions import HTTPException

from app.services.current_user import CurrentUser
from app.services.exceptions import ServiceError
from app.services.visits import VisitsService
from web.api.schemas import MarkVisitRequest, SearchVisitsRequests, VisitEventResponse, VisitsResponse
from web.utils import from_query


@post('', tags=['visits'], security=[{'user_auth': []}])
async def mark_visit(
    data: MarkVisitRequest,
    visits_service: VisitsService,
    current_user: CurrentUser,
) -> VisitEventResponse:
    try:
        visit = await visits_service.mark_visited(
            user_id=current_user.id,
            country_code=data.country_code,
            trip_date=data.trip_date,
        )
        return VisitEventResponse(**visit)
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@get(
    '',
    tags=['visits'],
    security=[{'user_auth': []}],
    dependencies={'filters': from_query(SearchVisitsRequests)},
    deprecated=True,
)
async def search_visits(
    visits_service: VisitsService,
    current_user: CurrentUser,
    filters: SearchVisitsRequests,
) -> VisitsResponse:
    data = await visits_service.search_visits(
        user_id=current_user.id,
        **{k: v for k, v in vars(filters).items() if v is not None},
    )
    return VisitsResponse(
        visits=[VisitEventResponse(**item) for item in data['visits']],
        visited_country_codes=data['visited_country_codes'],
    )


@patch('/{visit_id:uuid}', tags=['visits'], security=[{'user_auth': []}])
async def update_visit_by_id(
    visit_id: UUID,
    data: MarkVisitRequest,
    visits_service: VisitsService,
    current_user: CurrentUser,
) -> VisitEventResponse:
    try:
        visit = await visits_service.update_visit_by_id(
            visit_id=visit_id,
            user_id=current_user.id,
            country_code=data.country_code,
            trip_date=data.trip_date,
        )
        return VisitEventResponse(**visit)
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@delete('/{visit_id:uuid}', tags=['visits'], security=[{'user_auth': []}])
async def delete_visit_by_id(
    visit_id: UUID,
    visits_service: VisitsService,
    current_user: CurrentUser,
) -> None:
    try:
        await visits_service.delete_visit_by_id(
            visit_id=visit_id,
            user_id=current_user.id,
        )
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


visits_router = Router(
    path='/api/v1/visits', route_handlers=[mark_visit, search_visits, update_visit_by_id, delete_visit_by_id]
)
