from uuid import UUID

from litestar import Router, delete, get, patch, post

from app.services.current_user import CurrentUser
from app.services.exceptions import ServiceError
from app.services.visits_checklist import VisitsChecklistService
from web.api.visits_checklist.schemas import (
    CreateVisitChecklistRequest,
    PaginationResponse,
    UpdateVisitChecklistRequest,
    VisitChecklistResponse,
    VisitsChecklistListRequest,
    VisitsChecklistListResponse,
)
from web.utils import from_query


@post('', tags=['visits-checklist'], security=[{'user_auth': []}])
async def create_visit_checklist_item(
    data: CreateVisitChecklistRequest,
    visits_checklist_service: VisitsChecklistService,
    current_user: CurrentUser,
) -> VisitChecklistResponse:
    item = await visits_checklist_service.create_item(
        user_id=current_user.id,
        visit_id=data.visit_id,
        content=data.content,
    )
    return VisitChecklistResponse(**item)


@get(
    '',
    tags=['visits-checklist'],
    security=[{'user_auth': []}],
    dependencies={'filters': from_query(VisitsChecklistListRequest)},
)
async def list_visit_checklist_items(
    visits_checklist_service: VisitsChecklistService,
    current_user: CurrentUser,
    filters: VisitsChecklistListRequest,
) -> VisitsChecklistListResponse:
    data = await visits_checklist_service.list_items(
        user_id=current_user.id,
        **filters.to_repo_filters(),
    )
    return VisitsChecklistListResponse(
        items=[VisitChecklistResponse(**item) for item in data.items],
        pagination=PaginationResponse(
            limit=data.pagination.limit,
            offset=data.pagination.offset,
            total=data.pagination.total,
        ),
    )


@get('/{checklist_id:uuid}', tags=['visits-checklist'], security=[{'user_auth': []}])
async def get_visit_checklist_item_by_id(
    checklist_id: UUID,
    visits_checklist_service: VisitsChecklistService,
    current_user: CurrentUser,
) -> VisitChecklistResponse:
    item = await visits_checklist_service.get_item_by_id(checklist_id=checklist_id, user_id=current_user.id)
    return VisitChecklistResponse(**item)


@patch('/{checklist_id:uuid}', tags=['visits-checklist'], security=[{'user_auth': []}])
async def update_visit_checklist_item_by_id(
    checklist_id: UUID,
    data: UpdateVisitChecklistRequest,
    visits_checklist_service: VisitsChecklistService,
    current_user: CurrentUser,
) -> VisitChecklistResponse:
    payload = data.model_dump(exclude_unset=True)
    if not payload:
        raise ServiceError('No fields provided for update')

    item = await visits_checklist_service.update_item_by_id(
        checklist_id=checklist_id,
        user_id=current_user.id,
        **payload,
    )
    return VisitChecklistResponse(**item)


@delete('/{checklist_id:uuid}', tags=['visits-checklist'], security=[{'user_auth': []}], status_code=204)
async def delete_visit_checklist_item_by_id(
    checklist_id: UUID,
    visits_checklist_service: VisitsChecklistService,
    current_user: CurrentUser,
) -> None:
    await visits_checklist_service.delete_item_by_id(checklist_id=checklist_id, user_id=current_user.id)


visits_checklist_router = Router(
    path='/api/v1/visits/checklist',
    route_handlers=[
        create_visit_checklist_item,
        list_visit_checklist_items,
        get_visit_checklist_item_by_id,
        update_visit_checklist_item_by_id,
        delete_visit_checklist_item_by_id,
    ],
)
