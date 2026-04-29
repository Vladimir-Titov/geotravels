import asyncio
import logging
import re
from collections import Counter
from datetime import date
from typing import Any
from uuid import UUID, uuid7

from app.models.tables import FileVisibility, VisitStatus, VisitVisibility
from app.repositories.base import PaginatedResponse
from app.repositories.files import FilesRepository
from app.repositories.visits import VisitsRepository
from app.repositories.visits_cities import VisitsCitiesRepository
from app.services.exceptions import InvalidFileError, NotFoundError, ServiceError
from app.services.file_storage import FileStorage
from helpers import InvalidImageError, optimaze_image

logger = logging.getLogger(__name__)


class VisitsService:
    DEFAULT_TITLE = 'Untitled trip'
    DEFAULT_VISIBILITY = VisitVisibility.PRIVATE
    ALLOWED_VISIBILITIES = set(VisitVisibility)
    ALLOWED_STATUSES = {
        VisitStatus.PLANNED,
        VisitStatus.IN_TRIP,
        VisitStatus.VISITED,
    }

    def __init__(
        self,
        visits_repository: VisitsRepository,
        visits_cities_repository: VisitsCitiesRepository,
        files_repository: FilesRepository,
        file_storage: FileStorage | None = None,
    ):
        self.visits_repository = visits_repository
        self.visits_cities_repository = visits_cities_repository
        self.files_repository = files_repository
        self.file_storage = file_storage

    def _normalize_title(self, title: str | None) -> str:
        if title is None:
            return self.DEFAULT_TITLE

        normalized = title.strip()
        if not normalized:
            raise ServiceError('title cannot be empty')
        if len(normalized) > 80:
            raise ServiceError('title is too long, max length is 80')
        return normalized

    def _normalize_visibility(self, visibility: VisitVisibility | None) -> VisitVisibility:
        if visibility is None:
            return self.DEFAULT_VISIBILITY
        if visibility not in self.ALLOWED_VISIBILITIES:
            allowed_visibilities = ', '.join(item.value for item in VisitVisibility)
            raise ServiceError(f'visibility must be one of: {allowed_visibilities}')
        return visibility

    @staticmethod
    def _normalize_status(status: VisitStatus | None) -> VisitStatus:
        if status is None:
            return VisitStatus.VISITED
        if status not in VisitsService.ALLOWED_STATUSES:
            allowed_statuses = ', '.join(item.value for item in VisitStatus)
            raise ServiceError(f'status must be one of: {allowed_statuses}')
        return status

    @staticmethod
    def _deduplicate_city_ids(city_ids: list[UUID]) -> list[UUID]:
        return list(dict.fromkeys(city_ids))

    def _resolve_city_ids(
        self,
        city_ids: list[UUID] | None,
        city_id: UUID | None,
    ) -> list[UUID]:
        if city_ids is not None:
            return self._deduplicate_city_ids(city_ids)
        if city_id is None:
            return []
        return [city_id]

    @staticmethod
    def _resolve_primary_city_id(city_ids: list[UUID]) -> UUID | None:
        return city_ids[0] if city_ids else None

    @staticmethod
    def _validate_date_range(date_from: date | None, date_to: date | None) -> None:
        if date_from is not None and date_to is not None and date_to < date_from:
            raise ServiceError('date_to cannot be earlier than date_from')

    @staticmethod
    def _normalize_upload_filename(filename: str | None) -> str:
        candidate = (filename or 'photo.webp').strip()
        if not candidate:
            raise ServiceError('Filename cannot be empty')

        candidate = re.sub(r'[^A-Za-z0-9._-]+', '_', candidate)
        stem = candidate.rsplit('.', 1)[0] if '.' in candidate else candidate
        stem = stem.strip('._-') or 'photo'
        normalized = f'{stem}.webp'
        if len(normalized) > 64:
            raise ServiceError('Filename is too long, max length is 64')
        return normalized

    @staticmethod
    def _build_file_object_key(user_id: UUID, filename: str) -> str:
        return f'{user_id}/{uuid7()}_{filename}'

    async def _get_visit_or_raise(self, visit_id: UUID, user_id: UUID) -> dict[str, Any]:
        visit = await self.visits_repository.search_first_row(id=visit_id, user_id=user_id)
        if not visit:
            raise NotFoundError('Visit not found')
        return visit

    async def _ensure_cover_file_attached(self, cover_file_id: UUID, visit_id: UUID, user_id: UUID) -> None:
        attached = await self.files_repository.is_owned_file_attached_to_visit(
            file_id=cover_file_id,
            visit_id=visit_id,
            user_id=user_id,
        )
        if not attached:
            raise ServiceError('cover_file_id must reference a file attached to this visit')

    async def _enrich_visits(self, visits_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not visits_rows:
            return []

        visit_ids = [row['id'] for row in visits_rows]
        city_ids_by_visit = await self.visits_cities_repository.list_city_ids_for_visits(visit_ids)
        user_id = visits_rows[0].get('user_id')
        cover_file_ids_by_visit = await self.files_repository.list_cover_file_ids_for_visits(
            visit_ids=visit_ids,
            user_id=user_id if isinstance(user_id, UUID) else None,
        )

        enriched: list[dict[str, Any]] = []
        for row in visits_rows:
            item = dict(row)

            city_ids = city_ids_by_visit.get(item['id']) or []
            if not city_ids and item.get('city_id') is not None:
                city_ids = [item['city_id']]
            city_ids = self._deduplicate_city_ids(city_ids)

            item['title'] = item.get('title') or self.DEFAULT_TITLE
            item['visibility'] = item.get('visibility') or self.DEFAULT_VISIBILITY
            item['status'] = item.get('status') or VisitStatus.VISITED
            item['date_from'] = item.get('date_from')
            item['city_ids'] = city_ids
            item['city_id'] = self._resolve_primary_city_id(city_ids)
            item['cover_file_id'] = cover_file_ids_by_visit.get(item['id'])

            enriched.append(item)

        return enriched

    async def _enrich_visit(self, visit: dict[str, Any]) -> dict[str, Any]:
        enriched = await self._enrich_visits([visit])
        return enriched[0]

    async def create_visit(
        self,
        user_id: UUID,
        country_code: str,
        title: str | None = None,
        description: str | None = None,
        visibility: VisitVisibility = VisitVisibility.PRIVATE,
        status: VisitStatus | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        city_ids: list[UUID] | None = None,
        cover_file_id: UUID | None = None,
        city_id: UUID | None = None,  # backward compatibility (visit-v1)
    ) -> dict[str, Any]:
        resolved_title = self._normalize_title(title)
        resolved_visibility = self._normalize_visibility(visibility)
        resolved_status = self._normalize_status(status)
        resolved_date_from = date_from
        resolved_city_ids = self._resolve_city_ids(city_ids=city_ids, city_id=city_id)
        resolved_city_id = self._resolve_primary_city_id(resolved_city_ids)

        self._validate_date_range(date_from=resolved_date_from, date_to=date_to)

        async with self.visits_repository.transaction():
            created = await self.visits_repository.create(
                user_id=user_id,
                country_code=country_code,
                title=resolved_title,
                description=description,
                visibility=resolved_visibility,
                date_from=resolved_date_from,
                date_to=date_to,
                city_id=resolved_city_id,
                status=resolved_status,
            )
            await self.visits_cities_repository.replace_cities_for_visit(
                visit_id=created['id'],
                city_ids=resolved_city_ids,
            )
            if cover_file_id is not None:
                await self._ensure_cover_file_attached(
                    cover_file_id=cover_file_id,
                    visit_id=created['id'],
                    user_id=user_id,
                )
                await self.files_repository.set_cover_file_for_visit(
                    file_id=cover_file_id,
                    visit_id=created['id'],
                    user_id=user_id,
                )

        return await self._enrich_visit(created)

    async def list_visits(self, user_id: UUID, limit: int, offset: int, **filters: Any) -> PaginatedResponse:
        response = await self.visits_repository.paginated_search(
            order_by=['-created', '-id'],
            limit=limit,
            offset=offset,
            user_id=user_id,
            **filters,
        )
        return PaginatedResponse(
            items=await self._enrich_visits(response.items),
            pagination=response.pagination,
        )

    async def get_visit_by_id(self, visit_id: UUID, user_id: UUID) -> dict[str, Any]:
        visit = await self._get_visit_or_raise(visit_id=visit_id, user_id=user_id)
        return await self._enrich_visit(visit)

    async def update_visit_by_id(self, visit_id: UUID, user_id: UUID, **payload: Any) -> dict[str, Any]:
        existing = await self._get_visit_or_raise(visit_id=visit_id, user_id=user_id)

        has_city_ids = 'city_ids' in payload
        has_city_id = 'city_id' in payload
        has_cover_file_id = 'cover_file_id' in payload

        update_payload = dict(payload)
        provided_city_ids = update_payload.pop('city_ids', None)
        provided_city_id = update_payload.pop('city_id', None)
        cover_file_id = update_payload.pop('cover_file_id', None) if has_cover_file_id else None

        next_city_ids: list[UUID] | None = None
        if has_city_ids or has_city_id:
            next_city_ids = self._resolve_city_ids(
                city_ids=provided_city_ids if has_city_ids else None,
                city_id=provided_city_id if has_city_id else None,
            )
            update_payload['city_id'] = self._resolve_primary_city_id(next_city_ids)

        if 'title' in update_payload:
            update_payload['title'] = self._normalize_title(update_payload['title'])
        if 'visibility' in update_payload:
            update_payload['visibility'] = self._normalize_visibility(update_payload['visibility'])
        if 'status' in update_payload:
            update_payload['status'] = self._normalize_status(update_payload['status'])

        if has_cover_file_id:
            if cover_file_id is not None:
                await self._ensure_cover_file_attached(
                    cover_file_id=cover_file_id,
                    visit_id=visit_id,
                    user_id=user_id,
                )

        resulting_date_from = (
            update_payload['date_from'] if 'date_from' in update_payload else existing.get('date_from')
        )
        resulting_date_to = update_payload.get('date_to', existing.get('date_to'))
        self._validate_date_range(date_from=resulting_date_from, date_to=resulting_date_to)

        async with self.visits_repository.transaction():
            updated = existing
            if update_payload:
                updated = await self.visits_repository.update_by_id(entity_id=visit_id, **update_payload)
            if next_city_ids is not None:
                await self.visits_cities_repository.replace_cities_for_visit(
                    visit_id=visit_id,
                    city_ids=next_city_ids,
                )
            if has_cover_file_id:
                if cover_file_id is None:
                    await self.files_repository.clear_cover_for_visit(visit_id=visit_id, user_id=user_id)
                else:
                    await self.files_repository.set_cover_file_for_visit(
                        file_id=cover_file_id,
                        visit_id=visit_id,
                        user_id=user_id,
                    )

        return await self._enrich_visit(updated)

    async def delete_visit_by_id(self, visit_id: UUID, user_id: UUID) -> None:
        await self._get_visit_or_raise(visit_id=visit_id, user_id=user_id)
        await self.visits_repository.delete_by_id(entity_id=visit_id)

    async def upload_photo_for_visit(
        self,
        visit_id: UUID,
        user_id: UUID,
        content: bytes,
        filename: str | None = None,
        visibility: FileVisibility = FileVisibility.PRIVATE,
    ) -> dict[str, Any]:
        if not content:
            raise ServiceError('File content is empty')
        if self.file_storage is None:
            raise RuntimeError('File storage is not configured for visit uploads')

        await self._get_visit_or_raise(visit_id=visit_id, user_id=user_id)
        normalized_filename = self._normalize_upload_filename(filename)
        object_key = self._build_file_object_key(user_id=user_id, filename=normalized_filename)

        try:
            optimized_content = await asyncio.to_thread(optimaze_image, raw_image=content, quality=80)
        except InvalidImageError as exc:
            raise InvalidFileError('Uploaded file is not an image') from exc

        file_url = await self.file_storage.upload_file(
            key=object_key,
            content=optimized_content,
            file_type='image/webp',
        )

        try:
            async with self.visits_repository.transaction():
                file_row = await self.files_repository.create_file(
                    file_url=file_url,
                    filename=normalized_filename,
                    file_type='image/webp',
                )
                await self.files_repository.create_file_visit_relation(
                    file_id=file_row['id'],
                    visit_id=visit_id,
                    user_id=user_id,
                    visibility=visibility,
                )
        except Exception:
            logger.exception('Failed to persist visit photo metadata, rolling back uploaded object')
            try:
                await self.file_storage.delete_file(file_url)
            except Exception:  # noqa: BLE001
                logger.exception('Failed to rollback uploaded visit photo from storage')
            raise

        created = await self.files_repository.get_owned_file(file_id=file_row['id'], user_id=user_id)
        if not created:
            raise RuntimeError('File has been created but relation is missing')
        return created

    @staticmethod
    def _file_download_url(file_id: UUID | None) -> str | None:
        return f'/api/v1/files/{file_id}/download' if file_id else None

    async def list_visit_cards(
        self,
        user_id: UUID,
        status: VisitStatus | str,
        limit: int,
        offset: int,
    ) -> PaginatedResponse:
        if isinstance(status, str):
            try:
                status = VisitStatus(status)
            except ValueError as exc:
                raise ServiceError('status must be one of: visited, planned') from exc

        if status not in {VisitStatus.VISITED, VisitStatus.PLANNED}:
            raise ServiceError('status must be one of: visited, planned')

        response = await self.visits_repository.list_visit_cards(
            user_id=user_id,
            status=status,
            limit=limit,
            offset=offset,
        )
        items: list[dict[str, Any]] = []
        for row in response.items:
            item = dict(row)
            item['cover_url'] = self._file_download_url(item.pop('cover_file_id', None))
            items.append(item)
        return PaginatedResponse(items=items, pagination=response.pagination)

    async def get_visit_details(self, visit_id: UUID, user_id: UUID) -> dict[str, Any]:
        header = await self.visits_repository.get_visit_detail_header(visit_id=visit_id, user_id=user_id)
        if not header:
            raise NotFoundError('Visit not found')

        fallback_cover_file_id = header.get('cover_file_id')
        visit = await self._enrich_visit(header)
        if visit.get('cover_file_id') is None and fallback_cover_file_id is not None:
            visit['cover_file_id'] = fallback_cover_file_id
        photos = await self.visits_repository.list_visit_detail_photos(visit_id=visit_id, user_id=user_id)
        checklist = await self.visits_repository.list_visit_detail_checklist(visit_id=visit_id, user_id=user_id)
        places = await self.visits_repository.list_visit_detail_places(visit_id=visit_id, user_id=user_id)
        cities = await self.visits_repository.list_visit_detail_cities(visit_id=visit_id)

        if not cities and visit.get('city_id') and visit.get('city_name'):
            cities = [
                {
                    'id': visit['city_id'],
                    'name': visit['city_name'],
                    'country_code': visit['country_code'],
                }
            ]

        visit['cover_url'] = self._file_download_url(visit.get('cover_file_id'))
        return {
            'visit': visit,
            'photos': [
                {
                    **photo,
                    'file_url': self._file_download_url(photo['id']),
                }
                for photo in photos
            ],
            'checklist': checklist,
            'places': places,
            'cities': cities,
        }

    @staticmethod
    def _status_is(value: Any, expected: VisitStatus) -> bool:
        return value == expected or value == expected.value

    async def get_visit_statistics(self, user_id: UUID) -> dict[str, Any]:
        visits_rows = await self.visits_repository.list_user_visits_for_statistics(user_id=user_id)
        visited_rows = [row for row in visits_rows if self._status_is(row.get('status'), VisitStatus.VISITED)]
        planned_count = sum(1 for row in visits_rows if self._status_is(row.get('status'), VisitStatus.PLANNED))

        countries = Counter(str(row['country_code']) for row in visited_rows if row.get('country_code'))
        country_names: dict[str, str | None] = {
            str(row['country_code']): row.get('country_name') for row in visited_rows if row.get('country_code')
        }

        city_links = await self.visits_repository.list_user_visit_city_links_for_statistics(user_id=user_id)
        city_counts = Counter(str(row['city_id']) for row in city_links if row.get('city_id'))
        city_names: dict[str, str] = {
            str(row['city_id']): str(row['city_name'])
            for row in city_links
            if row.get('city_id') and row.get('city_name')
        }

        favorite_city = None
        if city_counts:
            favorite_city_id, favorite_count = sorted(
                city_counts.items(),
                key=lambda item: (-item[1], city_names.get(item[0], '')),
            )[0]
            favorite_city = {
                'city_id': UUID(favorite_city_id),
                'city_name': city_names.get(favorite_city_id, favorite_city_id),
                'visits_count': favorite_count,
            }

        trips_by_country = [
            {
                'country_name': country_names.get(country_code) or country_code,
                'trips_count': trips_count,
            }
            for country_code, trips_count in sorted(
                countries.items(),
                key=lambda item: (-item[1], country_names.get(item[0]) or item[0]),
            )
        ]

        return {
            'visited_count': len(visited_rows),
            'planned_count': planned_count,
            'countries_count': len(countries),
            'cities_count': len(city_counts),
            'repeated_countries_count': sum(1 for count in countries.values() if count > 1),
            'favorite_city': favorite_city,
            'trips_by_country': trips_by_country,
        }
