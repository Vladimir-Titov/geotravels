from uuid import UUID

from litestar import Router, delete, get, post

from app.services.current_user import CurrentUser
from app.services.visits_places_files import VisitsPlacesFilesService
from web.api.visits_places_files.schemas import (
    CreateVisitPlaceFileRequest,
    PaginationResponse,
    VisitPlaceFileResponse,
    VisitsPlacesFilesListRequest,
    VisitsPlacesFilesListResponse,
)
from web.utils import from_query


@post('', tags=['visits-places-files'], security=[{'user_auth': []}])
async def create_visit_place_file(
    data: CreateVisitPlaceFileRequest,
    visits_places_files_service: VisitsPlacesFilesService,
    current_user: CurrentUser,
) -> VisitPlaceFileResponse:
    relation = await visits_places_files_service.create_relation(
        user_id=current_user.id,
        visit_place_id=data.visit_place_id,
        file_id=data.file_id,
    )
    return VisitPlaceFileResponse(**relation)


@get(
    '',
    tags=['visits-places-files'],
    security=[{'user_auth': []}],
    dependencies={'filters': from_query(VisitsPlacesFilesListRequest)},
)
async def list_visit_place_files(
    visits_places_files_service: VisitsPlacesFilesService,
    current_user: CurrentUser,
    filters: VisitsPlacesFilesListRequest,
) -> VisitsPlacesFilesListResponse:
    data = await visits_places_files_service.list_relations(
        user_id=current_user.id,
        **filters.to_repo_filters(),
    )
    return VisitsPlacesFilesListResponse(
        items=[VisitPlaceFileResponse(**item) for item in data.items],
        pagination=PaginationResponse(
            limit=data.pagination.limit,
            offset=data.pagination.offset,
            total=data.pagination.total,
        ),
    )


@get('/{relation_id:uuid}', tags=['visits-places-files'], security=[{'user_auth': []}])
async def get_visit_place_file_by_id(
    relation_id: UUID,
    visits_places_files_service: VisitsPlacesFilesService,
    current_user: CurrentUser,
) -> VisitPlaceFileResponse:
    relation = await visits_places_files_service.get_relation_by_id(relation_id=relation_id, user_id=current_user.id)
    return VisitPlaceFileResponse(**relation)


@delete('/{relation_id:uuid}', tags=['visits-places-files'], security=[{'user_auth': []}], status_code=204)
async def delete_visit_place_file_by_id(
    relation_id: UUID,
    visits_places_files_service: VisitsPlacesFilesService,
    current_user: CurrentUser,
) -> None:
    await visits_places_files_service.delete_relation_by_id(relation_id=relation_id, user_id=current_user.id)


visits_places_files_router = Router(
    path='/api/v1/visits/places-files',
    route_handlers=[
        create_visit_place_file,
        list_visit_place_files,
        get_visit_place_file_by_id,
        delete_visit_place_file_by_id,
    ],
)
