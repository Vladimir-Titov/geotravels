from uuid import UUID

from litestar import Request, Response, Router, delete, get, patch
from litestar.openapi.datastructures import ResponseSpec

from app.services.current_user import CurrentUser
from app.services.files import FilesService
from app.services.http_cache import matches_etag
from app.services.image_variants import ImageVariant
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
    request: Request,
    variant: ImageVariant = ImageVariant.FULL,
) -> Response[bytes]:
    file_data = await files_service.download_file(file_id=file_id, user_id=current_user.id, variant=variant)

    max_age = 86400 if variant in {ImageVariant.THUMB, ImageVariant.PREVIEW} else 3600
    headers: dict[str, str] = {
        'Cache-Control': f'private, max-age={max_age}',
        'ETag': file_data['etag'],
    }
    if file_data['filename']:
        headers['Content-Disposition'] = f'attachment; filename="{file_data["filename"]}"'

    if matches_etag(request.headers.get('If-None-Match'), file_data['etag']):
        return Response(
            content=b'',
            status_code=304,
            media_type=file_data['file_type'] or 'application/octet-stream',
            headers=headers,
        )

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
    route_handlers=[update_file, delete_file, download_file, list_my_files, list_public_user_files],
)
