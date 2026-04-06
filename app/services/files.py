from __future__ import annotations

import logging
import re
from uuid import UUID, uuid7

from app.repositories.base import PaginatedResponse
from app.repositories.files import FilesRepository
from app.repositories.visits import VisitsRepository
from app.services.exceptions import NotFoundError, ServiceError
from app.services.file_storage import FileStorage

logger = logging.getLogger(__name__)


class FilesService:
    def __init__(
        self,
        files_repository: FilesRepository,
        visits_repository: VisitsRepository,
        file_storage: FileStorage,
    ):
        self.files_repository = files_repository
        self.visits_repository = visits_repository
        self.file_storage = file_storage

    def _normalize_filename(self, filename: str | None) -> str:
        candidate = (filename or 'photo.jpg').strip()
        if not candidate:
            raise ServiceError('Filename cannot be empty')

        candidate = re.sub(r'[^A-Za-z0-9._-]+', '_', candidate)
        if len(candidate) > 64:
            raise ServiceError('Filename is too long, max length is 64')
        return candidate

    def _build_object_key(self, user_id: UUID, filename: str) -> str:
        return f'{user_id}/{uuid7()}_{filename}'

    async def _ensure_visit_owned(self, visit_id: UUID, user_id: UUID) -> None:
        visit = await self.visits_repository.search_first_row(id=visit_id, user_id=user_id)
        if not visit:
            raise NotFoundError('Visit not found')

    async def create_file_for_visit(
        self,
        user_id: UUID,
        visit_id: UUID,
        content: bytes,
        filename: str | None = None,
        file_type: str | None = None,
        is_private: bool = False,
    ) -> dict:
        if not content:
            raise ServiceError('File content is empty')

        await self._ensure_visit_owned(visit_id=visit_id, user_id=user_id)
        normalized_filename = self._normalize_filename(filename)
        object_key = self._build_object_key(user_id=user_id, filename=normalized_filename)

        file_url = await self.file_storage.upload_file(
            key=object_key,
            content=content,
            file_type=file_type,
        )

        try:
            async with self.files_repository.transaction():
                file_row = await self.files_repository.create_file(
                    file_url=file_url,
                    filename=normalized_filename,
                    file_type=file_type,
                )
                await self.files_repository.create_file_visit_relation(
                    file_id=file_row['id'],
                    visit_id=visit_id,
                    user_id=user_id,
                    is_private=is_private,
                )
        except Exception:
            logger.exception('Failed to persist file metadata, rolling back uploaded object')
            try:
                await self.file_storage.delete_file(file_url)
            except Exception:  # noqa: BLE001
                logger.exception('Failed to rollback uploaded file from storage')
            raise

        created = await self.files_repository.get_owned_file(file_id=file_row['id'], user_id=user_id)
        if not created:
            raise RuntimeError('File has been created but relation is missing')
        return created

    async def update_filename(self, file_id: UUID, user_id: UUID, filename: str) -> dict:
        existing = await self.files_repository.get_owned_file(file_id=file_id, user_id=user_id)
        if not existing:
            raise NotFoundError('File not found')

        normalized_filename = self._normalize_filename(filename)
        await self.files_repository.update_filename(file_id=file_id, filename=normalized_filename)

        updated = await self.files_repository.get_owned_file(file_id=file_id, user_id=user_id)
        if not updated:
            raise RuntimeError('File has been updated but relation is missing')
        return updated

    async def delete_file(self, file_id: UUID, user_id: UUID) -> dict:
        existing = await self.files_repository.get_owned_file(file_id=file_id, user_id=user_id)
        if not existing:
            raise NotFoundError('File not found')

        should_delete_binary = False
        async with self.files_repository.transaction():
            deleted = await self.files_repository.delete_owned_relation(file_id=file_id, user_id=user_id)
            if not deleted:
                raise NotFoundError('File not found')

            left_relations = await self.files_repository.count_relations(file_id=file_id)
            if left_relations == 0:
                should_delete_binary = True
                await self.files_repository.delete_file(file_id=file_id)

        if should_delete_binary:
            try:
                await self.file_storage.delete_file(existing['file_url'])
            except Exception:  # noqa: BLE001
                logger.exception('Failed to remove file from storage for %s', existing['file_url'])

        return existing

    async def list_my_files(self, user_id: UUID, limit: int, offset: int, visit_id: UUID | None) -> PaginatedResponse:
        return await self.files_repository.list_files_by_user(
            user_id=user_id,
            visit_id=visit_id,
            include_private=True,
            limit=limit,
            offset=offset,
        )

    async def list_public_files_of_user(
        self,
        target_user_id: UUID,
        limit: int,
        offset: int,
        visit_id: UUID | None,
    ) -> PaginatedResponse:
        return await self.files_repository.list_files_by_user(
            user_id=target_user_id,
            visit_id=visit_id,
            include_private=False,
            limit=limit,
            offset=offset,
        )
