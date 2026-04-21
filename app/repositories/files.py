from __future__ import annotations

from typing import Any
from uuid import UUID, uuid7

from sqlalchemy import func, select

from app.models.tables import files, files_visits
from app.repositories.base import BaseDBRepository, PaginatedResponse, Pagination


class FilesRepository(BaseDBRepository):
    @staticmethod
    def _base_file_query() -> Any:
        return select(
            files.c.id,
            files.c.file_url,
            files.c.filename,
            files.c.file_type,
            files_visits.c.visit_id,
            files_visits.c.user_id,
            files_visits.c.is_private,
        ).select_from(files_visits.join(files, files_visits.c.file_id == files.c.id))

    @staticmethod
    def _normalize_file_row(row: dict[str, Any]) -> dict[str, Any]:
        if isinstance(row.get('id'), str):
            row['id'] = UUID(row['id'])
        if isinstance(row.get('file_id'), str):
            row['file_id'] = UUID(row['file_id'])
        if isinstance(row.get('visit_id'), str):
            row['visit_id'] = UUID(row['visit_id'])
        if isinstance(row.get('user_id'), str):
            row['user_id'] = UUID(row['user_id'])
        return row

    async def create_file(
        self,
        file_url: str,
        filename: str | None,
        file_type: str | None,
    ) -> dict[str, Any]:
        query = (
            files.insert()
            .values(
                id=uuid7(),
                file_url=file_url,
                filename=filename,
                file_type=file_type,
            )
            .returning(files)
        )
        row = await self.fetchrow(query)
        if not row:
            raise RuntimeError('No row has been created for file')
        return self._normalize_file_row(row)

    async def create_file_visit_relation(
        self,
        file_id: UUID,
        visit_id: UUID,
        user_id: UUID,
        is_private: bool,
    ) -> dict[str, Any]:
        query = (
            files_visits.insert()
            .values(
                id=uuid7(),
                file_id=file_id,
                visit_id=visit_id,
                user_id=user_id,
                is_private=is_private,
            )
            .returning(files_visits)
        )
        row = await self.fetchrow(query)
        if not row:
            raise RuntimeError('No row has been created for file relation')
        return self._normalize_file_row(row)

    async def get_owned_file(self, file_id: UUID, user_id: UUID) -> dict[str, Any] | None:
        query = self._base_file_query().where(
            files.c.id == file_id,
            files_visits.c.user_id == user_id,
        )
        row = await self.fetchrow(query)
        if not row:
            return None
        return self._normalize_file_row(row)

    async def is_owned_file_attached_to_visit(self, file_id: UUID, visit_id: UUID, user_id: UUID) -> bool:
        query = select(files_visits.c.id).where(
            files_visits.c.file_id == file_id,
            files_visits.c.visit_id == visit_id,
            files_visits.c.user_id == user_id,
        )
        row = await self.fetchrow(query)
        return row is not None

    async def list_files_by_user(
        self,
        user_id: UUID,
        limit: int,
        offset: int,
        visit_id: UUID | None = None,
        include_private: bool = True,
    ) -> PaginatedResponse:
        conditions = [files_visits.c.user_id == user_id]
        if visit_id is not None:
            conditions.append(files_visits.c.visit_id == visit_id)
        if not include_private:
            conditions.append(files_visits.c.is_private.is_(False))

        query = (
            self._base_file_query()
            .where(*conditions)
            .order_by(files_visits.c.id.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = await self.fetch(query)

        count_query = select(func.count()).select_from(
            files_visits.join(files, files_visits.c.file_id == files.c.id)
        )
        count_query = count_query.where(*conditions)
        total = await self.fetchval(count_query)

        return PaginatedResponse(
            items=[self._normalize_file_row(row) for row in rows],
            pagination=Pagination(limit=limit, offset=offset, total=int(total or 0)),
        )

    async def update_filename(self, file_id: UUID, filename: str) -> dict[str, Any]:
        query = files.update().where(files.c.id == file_id).values(filename=filename).returning(files)
        row = await self.fetchrow(query)
        if not row:
            raise RuntimeError('No row has been updated for file')
        return self._normalize_file_row(row)

    async def delete_owned_relation(self, file_id: UUID, user_id: UUID) -> bool:
        query = select(files_visits.c.id).where(
            files_visits.c.file_id == file_id,
            files_visits.c.user_id == user_id,
        )
        relation = await self.fetchrow(query)
        if not relation:
            return False

        delete_query = files_visits.delete().where(
            files_visits.c.file_id == file_id,
            files_visits.c.user_id == user_id,
        )
        await self.fetchval(delete_query)
        return True

    async def count_relations(self, file_id: UUID) -> int:
        query = select(func.count()).select_from(files_visits).where(files_visits.c.file_id == file_id)
        total = await self.fetchval(query)
        return int(total or 0)

    async def delete_file(self, file_id: UUID) -> bool:
        query = select(files.c.id).where(files.c.id == file_id)
        row = await self.fetchrow(query)
        if not row:
            return False

        delete_query = files.delete().where(files.c.id == file_id)
        await self.fetchval(delete_query)
        return True
