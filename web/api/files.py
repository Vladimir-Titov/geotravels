from __future__ import annotations

from typing import Annotated
from uuid import UUID

from litestar import Response, Router, delete, get, patch, post
from litestar.enums import RequestEncodingType
from litestar.openapi.datastructures import ResponseSpec
from litestar.params import Body

from app.services.current_user import CurrentUser
from app.services.exceptions import ServiceError
from app.services.files import FilesService
from web.api.schemas import (
    FilesListRequest,
    FilesListResponse,
    PaginationResponse,
    UpdateFileRequest,
    UploadFileRequest,
    VisitFileResponse,
)
from web.utils import from_query


@post('', tags=['files'], security=[{'user_auth': []}])
async def upload_file(
    data: Annotated[UploadFileRequest, Body(media_type=RequestEncodingType.MULTI_PART)],
    files_service: FilesService,
    current_user: CurrentUser,
) -> VisitFileResponse:
    content = await data.file.read()
    if not content:
        raise ServiceError('File content is empty')

    filename = data.filename.strip() if data.filename is not None else data.file.filename
    if filename == '':
        filename = data.file.filename
    file_type = data.file_type.strip() if data.file_type is not None else data.file.content_type

    created = await files_service.create_file_for_visit(
        user_id=current_user.id,
        visit_id=data.visit_id,
        content=content,
        filename=filename,
        file_type=file_type,
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
    '/{file_id:uuid}/download',
    tags=['files'],
    security=[{'user_auth': []}],
    responses={
        200: ResponseSpec(
            data_container=bytes,
            media_type='application/octet-stream',
            description='File content',
        )
    },
)
async def download_file(
    file_id: UUID,
    files_service: FilesService,
    current_user: CurrentUser,
) -> Response[bytes]:
    file_data = await files_service.download_file(file_id=file_id, user_id=current_user.id)

    headers: dict[str, str] = {}
    if file_data['filename']:
        headers['Content-Disposition'] = f'attachment; filename="{file_data["filename"]}"'

    return Response(
        content=file_data['content'],
        media_type=file_data['file_type'] or 'application/octet-stream',
        headers=headers,
    )


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
    route_handlers=[upload_file, update_file, delete_file, download_file, list_my_files, list_public_user_files],
)
