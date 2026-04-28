from uuid import UUID

from litestar import Router, delete, get, patch, post

from app.services.current_user import CurrentUser
from app.services.exceptions import ServiceError
from app.services.visits_places import VisitsPlacesService
from web.api.schemas import (
    CreateVisitPlaceRequest,
    PaginationResponse,
    UpdateVisitPlaceRequest,
    VisitPlaceResponse,
    VisitsPlacesListRequest,
    VisitsPlacesListResponse,
)
from web.utils import from_query


@post('', tags=['visits-places'], security=[{'user_auth': []}])
async def create_visit_place(
    data: CreateVisitPlaceRequest,
    visits_places_service: VisitsPlacesService,
    current_user: CurrentUser,
) -> VisitPlaceResponse:
    place = await visits_places_service.create_place(
        user_id=current_user.id,
        visit_id=data.visit_id,
        title=data.title,
    )
    return VisitPlaceResponse(**place)


@get(
    '',
    tags=['visits-places'],
    security=[{'user_auth': []}],
    dependencies={'filters': from_query(VisitsPlacesListRequest)},
)
async def list_visit_places(
    visits_places_service: VisitsPlacesService,
    current_user: CurrentUser,
    filters: VisitsPlacesListRequest,
) -> VisitsPlacesListResponse:
    data = await visits_places_service.list_places(
        user_id=current_user.id,
        **filters.to_repo_filters(),
    )
    return VisitsPlacesListResponse(
        items=[VisitPlaceResponse(**item) for item in data.items],
        pagination=PaginationResponse(
            limit=data.pagination.limit,
            offset=data.pagination.offset,
            total=data.pagination.total,
        ),
    )


@get('/{place_id:uuid}', tags=['visits-places'], security=[{'user_auth': []}])
async def get_visit_place_by_id(
    place_id: UUID,
    visits_places_service: VisitsPlacesService,
    current_user: CurrentUser,
) -> VisitPlaceResponse:
    place = await visits_places_service.get_place_by_id(place_id=place_id, user_id=current_user.id)
    return VisitPlaceResponse(**place)


@patch('/{place_id:uuid}', tags=['visits-places'], security=[{'user_auth': []}])
async def update_visit_place_by_id(
    place_id: UUID,
    data: UpdateVisitPlaceRequest,
    visits_places_service: VisitsPlacesService,
    current_user: CurrentUser,
) -> VisitPlaceResponse:
    payload = data.model_dump(exclude_unset=True)
    if not payload:
        raise ServiceError('No fields provided for update')

    place = await visits_places_service.update_place_by_id(
        place_id=place_id,
        user_id=current_user.id,
        **payload,
    )
    return VisitPlaceResponse(**place)


@delete('/{place_id:uuid}', tags=['visits-places'], security=[{'user_auth': []}], status_code=204)
async def delete_visit_place_by_id(
    place_id: UUID,
    visits_places_service: VisitsPlacesService,
    current_user: CurrentUser,
) -> None:
    await visits_places_service.delete_place_by_id(place_id=place_id, user_id=current_user.id)


visits_places_router = Router(
    path='/api/v1/visits/places',
    route_handlers=[
        create_visit_place,
        list_visit_places,
        get_visit_place_by_id,
        update_visit_place_by_id,
        delete_visit_place_by_id,
    ],
)
