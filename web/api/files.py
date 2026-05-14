from uuid import UUID

from litestar import Router, delete, get, patch

from app.services.current_user import CurrentUser
from app.services.files import FilesService
from web.api.schemas import (
    FilesListRequest,
    FilesListResponse,
    PaginationResponse,
    UpdateFileRequest,
    VisitFileResponse,
)
from web.utils import from_query


@patch('/{file_id:uuid}', tags=['files'], security=[{'user_auth': []}])
async def update_file(
    file_id: UUID,
    data: UpdateFileRequest,
    files_service: FilesService,
    current_user: CurrentUser,
) -> VisitFileResponse:
    updated = await files_service.update_filename(
        file_id=file_id,
        user_id=current_user.id,
        filename=data.filename,
    )
    return VisitFileResponse(**updated)


@delete('/{file_id:uuid}', tags=['files'], security=[{'user_auth': []}], status_code=200)
async def delete_file(
    file_id: UUID,
    files_service: FilesService,
    current_user: CurrentUser,
) -> VisitFileResponse:
    deleted = await files_service.delete_file(file_id=file_id, user_id=current_user.id)
    return VisitFileResponse(**deleted)


@get(
    '/mine',
    tags=['files'],
    security=[{'user_auth': []}],
    dependencies={'filters': from_query(FilesListRequest)},
)
async def list_my_files(
    files_service: FilesService,
    current_user: CurrentUser,
    filters: FilesListRequest,
) -> FilesListResponse:
    data = await files_service.list_my_files(
        user_id=current_user.id,
        limit=filters.limit,
        offset=filters.offset,
        visit_id=filters.visit_id,
    )
    return FilesListResponse(
        items=[VisitFileResponse(**item) for item in data.items],
        pagination=PaginationResponse(
            limit=data.pagination.limit,
            offset=data.pagination.offset,
            total=data.pagination.total,
        ),
    )


@get(
    '/users/{user_id:uuid}',
    tags=['files'],
    security=[{'user_auth': []}],
    dependencies={'filters': from_query(FilesListRequest)},
)
async def list_public_user_files(
    user_id: UUID,
    files_service: FilesService,
    current_user: CurrentUser,  # noqa: ARG001
    filters: FilesListRequest,
) -> FilesListResponse:
    data = await files_service.list_public_files_of_user(
        target_user_id=user_id,
        limit=filters.limit,
        offset=filters.offset,
        visit_id=filters.visit_id,
    )
    return FilesListResponse(
        items=[VisitFileResponse(**item) for item in data.items],
        pagination=PaginationResponse(
            limit=data.pagination.limit,
            offset=data.pagination.offset,
            total=data.pagination.total,
        ),
    )


files_router = Router(
    path='/api/v1/files',
    route_handlers=[update_file, delete_file, list_my_files, list_public_user_files],
)
