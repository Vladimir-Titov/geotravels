from typing import Annotated
from uuid import UUID

from litestar import Router, delete, get, patch, post
from litestar.enums import RequestEncodingType
from litestar.params import Body

from app.models import VisitStatus
from app.services.current_user import CurrentUser
from app.services.exceptions import ServiceError
from app.services.visits import VisitsService
from web.api.visits.schemas import (
    MarkVisitRequest,
    PaginationResponse,
    UpdateVisitRequest,
    UploadFileRequest,
    VisitCardsListResponse,
    VisitDetailsResponse,
    VisitEventResponse,
    VisitFileResponse,
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
        trip_start=data.trip_start,
        trip_end=data.trip_end,
        city_ids=data.city_ids,
        cover_file_id=data.cover_file_id,
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


@post('/{visit_id:uuid}/file', tags=['visits'], security=[{'user_auth': []}])
async def upload_photo_for_visit(
    visit_id: UUID,
    data: Annotated[UploadFileRequest, Body(media_type=RequestEncodingType.MULTI_PART)],
    visits_service: VisitsService,
    current_user: CurrentUser,
) -> VisitFileResponse:
    content = await data.file.read()
    if not content:
        raise ServiceError('File content is empty')

    filename = data.filename.strip() if data.filename is not None else data.file.filename
    if filename == '':
        filename = data.file.filename

    created = await visits_service.upload_photo_for_visit(
        user_id=current_user.id,
        visit_id=visit_id,
        content=content,
        filename=filename,
        visibility=data.visibility,
    )
    return VisitFileResponse(**created)


visits_router = Router(
    path='/api/v1/visits',
    route_handlers=[
        create_visit,
        list_visits,
        list_visit_cards,
        get_visit_statistics,
        get_visit_details,
        upload_photo_for_visit,
        get_visit_by_id,
        update_visit_by_id,
        delete_visit_by_id,
    ],
)
