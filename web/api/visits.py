from uuid import UUID

from litestar import Router, delete, get, patch, post

from app.services.current_user import CurrentUser
from app.services.exceptions import ServiceError
from app.services.visits import VisitsService
from web.api.schemas import (
    MarkVisitRequest,
    PaginationResponse,
    UpdateVisitRequest,
    VisitEventResponse,
    VisitsListRequest,
    VisitsListResponse,
)
from web.utils import from_query


@post('', tags=['visits'], security=[{'user_auth': []}])
async def create_visit(
    data: MarkVisitRequest,
    visits_service: VisitsService,
    current_user: CurrentUser,
) -> VisitEventResponse:
    visit = await visits_service.create_visit(
        user_id=current_user.id,
        country_code=data.country_code,
        title=data.title,
        description=data.description,
        visibility=data.visibility,
        date_from=data.date_from,
        date_to=data.date_to,
        city_ids=data.city_ids,
        cover_file_id=data.cover_file_id,
        city_id=data.city_id,
        trip_date=data.trip_date,
    )
    return VisitEventResponse(**visit)


@get(
    '',
    tags=['visits'],
    security=[{'user_auth': []}],
    dependencies={'filters': from_query(VisitsListRequest)},
)
async def list_visits(
    visits_service: VisitsService,
    current_user: CurrentUser,
    filters: VisitsListRequest,
) -> VisitsListResponse:
    data = await visits_service.list_visits(user_id=current_user.id, **filters.to_repo_filters())
    return VisitsListResponse(
        items=[VisitEventResponse(**item) for item in data.items],
        pagination=PaginationResponse(
            limit=data.pagination.limit,
            offset=data.pagination.offset,
            total=data.pagination.total,
        ),
    )


@get('/{visit_id:uuid}', tags=['visits'], security=[{'user_auth': []}])
async def get_visit_by_id(
    visit_id: UUID,
    visits_service: VisitsService,
    current_user: CurrentUser,
) -> VisitEventResponse:
    visit = await visits_service.get_visit_by_id(visit_id=visit_id, user_id=current_user.id)
    return VisitEventResponse(**visit)


@patch('/{visit_id:uuid}', tags=['visits'], security=[{'user_auth': []}])
async def update_visit_by_id(
    visit_id: UUID,
    data: UpdateVisitRequest,
    visits_service: VisitsService,
    current_user: CurrentUser,
) -> VisitEventResponse:
    payload = data.model_dump(exclude_unset=True)
    if not payload:
        raise ServiceError('No fields provided for update')

    visit = await visits_service.update_visit_by_id(
        visit_id=visit_id,
        user_id=current_user.id,
        **payload,
    )
    return VisitEventResponse(**visit)


@delete('/{visit_id:uuid}', tags=['visits'], security=[{'user_auth': []}])
async def delete_visit_by_id(
    visit_id: UUID,
    visits_service: VisitsService,
    current_user: CurrentUser,
) -> None:
    await visits_service.delete_visit_by_id(
        visit_id=visit_id,
        user_id=current_user.id,
    )


visits_router = Router(
    path='/api/v1/visits',
    route_handlers=[create_visit, list_visits, get_visit_by_id, update_visit_by_id, delete_visit_by_id],
)
