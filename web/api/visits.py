from uuid import UUID

from litestar import Router, delete, get, patch, post

from app.models.tables import VisitStatus
from app.services.current_user import CurrentUser
from app.services.exceptions import ServiceError
from app.services.visits import VisitsService
from web.api.schemas import (
    MarkVisitRequest,
    PaginationResponse,
    UpdateVisitRequest,
    VisitCardsListResponse,
    VisitDetailsResponse,
    VisitEventResponse,
    VisitsListRequest,
    VisitsListResponse,
    VisitStatisticsResponse,
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
        status=data.status,
        date_from=data.date_from,
        date_to=data.date_to,
        city_ids=data.city_ids,
        cover_file_id=data.cover_file_id,
        city_id=data.city_id,
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


@get(
    '/cards',
    tags=['visits'],
    security=[{'user_auth': []}],
)
async def list_visit_cards(
    visits_service: VisitsService,
    current_user: CurrentUser,
    status: VisitStatus,
    limit: int = 100,
    offset: int = 0,
) -> VisitCardsListResponse:
    data = await visits_service.list_visit_cards(
        user_id=current_user.id,
        status=status,
        limit=limit,
        offset=offset,
    )
    return VisitCardsListResponse(
        items=data.items,
        pagination=PaginationResponse(
            limit=data.pagination.limit,
            offset=data.pagination.offset,
            total=data.pagination.total,
        ),
    )


@get('/statistics', tags=['visits'], security=[{'user_auth': []}])
async def get_visit_statistics(
    visits_service: VisitsService,
    current_user: CurrentUser,
) -> VisitStatisticsResponse:
    statistics = await visits_service.get_visit_statistics(user_id=current_user.id)
    return VisitStatisticsResponse(**statistics)


@get('/{visit_id:uuid}/details', tags=['visits'], security=[{'user_auth': []}])
async def get_visit_details(
    visit_id: UUID,
    visits_service: VisitsService,
    current_user: CurrentUser,
) -> VisitDetailsResponse:
    details = await visits_service.get_visit_details(visit_id=visit_id, user_id=current_user.id)
    return VisitDetailsResponse(**details)


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
    route_handlers=[
        create_visit,
        list_visits,
        list_visit_cards,
        get_visit_statistics,
        get_visit_details,
        get_visit_by_id,
        update_visit_by_id,
        delete_visit_by_id,
    ],
)
