from __future__ import annotations

from uuid import UUID

from litestar import Request, Router, delete, get, patch, post
from litestar.datastructures import UploadFile

from app.services.current_user import CurrentUser
from app.services.exceptions import ServiceError
from app.services.files import FilesService
from web.api.schemas import (
    FilesListRequest,
    FilesListResponse,
    PaginationResponse,
    UpdateFileRequest,
    VisitFileResponse,
)
from web.utils import from_query


def _parse_bool(value: object, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value

    normalized = str(value).strip().lower()
    if normalized in {'1', 'true', 'yes', 'y', 'on'}:
        return True
    if normalized in {'0', 'false', 'no', 'n', 'off'}:
        return False
    raise ServiceError('Invalid is_private value')


@post('', tags=['files'], security=[{'user_auth': []}])
async def create_file(
    request: Request,
    files_service: FilesService,
    current_user: CurrentUser,
) -> VisitFileResponse:
    form = await request.form()

    visit_id_raw = form.get('visit_id')
    if visit_id_raw is None:
        raise ServiceError('visit_id is required')

    try:
        visit_id = UUID(str(visit_id_raw))
    except ValueError as exc:
        raise ServiceError('visit_id must be UUID') from exc

    file = form.get('file')
    if not isinstance(file, UploadFile):
        raise ServiceError('file is required')

    content = await file.read()
    if not content:
        raise ServiceError('File content is empty')

    filename = str(form.get('filename')).strip() if form.get('filename') is not None else file.filename
    file_type = str(form.get('file_type')).strip() if form.get('file_type') is not None else file.content_type
    is_private = _parse_bool(form.get('is_private'), default=False)

    created = await files_service.create_file_for_visit(
        user_id=current_user.id,
        visit_id=visit_id,
        content=content,
        filename=filename,
        file_type=file_type,
        is_private=is_private,
    )
    return VisitFileResponse(**created)


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
    route_handlers=[create_file, update_file, delete_file, list_my_files, list_public_user_files],
)
