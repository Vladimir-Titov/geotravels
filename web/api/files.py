from __future__ import annotations

import base64
import binascii
from uuid import UUID

from litestar import Router, delete, get, patch, post

from app.services.current_user import CurrentUser
from app.services.exceptions import ServiceError
from app.services.files import FilesService
from web.api.schemas import (
    CreateVisitFileRequest,
    FilesListRequest,
    FilesListResponse,
    PaginationResponse,
    UpdateFileRequest,
    VisitFileResponse,
)
from web.utils import from_query


def _decode_file_content(content_base64: str) -> bytes:
    try:
        decoded = base64.b64decode(content_base64, validate=True)
    except binascii.Error as exc:
        raise ServiceError('Invalid base64 file content') from exc

    if not decoded:
        raise ServiceError('File content is empty')
    return decoded


@post('', tags=['files'], security=[{'user_auth': []}])
async def create_file(
    data: CreateVisitFileRequest,
    files_service: FilesService,
    current_user: CurrentUser,
) -> VisitFileResponse:
    created = await files_service.create_file_for_visit(
        user_id=current_user.id,
        visit_id=data.visit_id,
        content=_decode_file_content(data.content_base64),
        filename=data.filename,
        file_type=data.file_type,
        is_private=data.is_private,
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
