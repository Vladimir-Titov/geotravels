from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any
from uuid import UUID

from app.repositories.base import PaginatedResponse
from app.repositories.files import FilesRepository
from app.repositories.visits import VisitsRepository
from app.repositories.visits_cities import VisitsCitiesRepository
from app.services.exceptions import NotFoundError, ServiceError


class VisitsService:
    VISIBILITY_PRIVATE = 'private'
    VISIBILITY_FOLLOWERS = 'followers'
    VISIBILITY_PUBLIC = 'public'
    DEFAULT_TITLE = 'Untitled story'
    ALLOWED_VISIBILITIES = {
        VISIBILITY_PRIVATE,
        VISIBILITY_FOLLOWERS,
        VISIBILITY_PUBLIC,
    }

    def __init__(
        self,
        visits_repository: VisitsRepository,
        visits_cities_repository: VisitsCitiesRepository,
        files_repository: FilesRepository,
    ):
        self.visits_repository = visits_repository
        self.visits_cities_repository = visits_cities_repository
        self.files_repository = files_repository

    def _normalize_title(self, title: str | None) -> str:
        if title is None:
            return self.DEFAULT_TITLE

        normalized = title.strip()
        if not normalized:
            raise ServiceError('title cannot be empty')
        if len(normalized) > 80:
            raise ServiceError('title is too long, max length is 80')
        return normalized

    def _normalize_visibility(self, visibility: str | None) -> str:
        if visibility is None:
            return self.VISIBILITY_PRIVATE
        if visibility not in self.ALLOWED_VISIBILITIES:
            raise ServiceError('visibility must be one of: private, followers, public')
        return visibility

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
    def _resolve_date_from(date_from: date | None, trip_date: date | None) -> date:
        return date_from or trip_date or datetime.now(UTC).date()

    @staticmethod
    def _resolve_trip_date(date_from: date, trip_date: date | None) -> date:
        return trip_date or date_from

    @staticmethod
    def _validate_date_range(date_from: date, date_to: date | None) -> None:
        if date_to is not None and date_to < date_from:
            raise ServiceError('date_to cannot be earlier than date_from')

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

        enriched: list[dict[str, Any]] = []
        for row in visits_rows:
            item = dict(row)

            city_ids = city_ids_by_visit.get(item['id']) or []
            if not city_ids and item.get('city_id') is not None:
                city_ids = [item['city_id']]
            city_ids = self._deduplicate_city_ids(city_ids)

            item['title'] = item.get('title') or self.DEFAULT_TITLE
            item['visibility'] = item.get('visibility') or self.VISIBILITY_PRIVATE
            item['date_from'] = item.get('date_from') or item.get('trip_date') or datetime.now(UTC).date()
            item['trip_date'] = item.get('trip_date') or item['date_from']
            item['city_ids'] = city_ids
            item['city_id'] = self._resolve_primary_city_id(city_ids)

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
        visibility: str = VISIBILITY_PRIVATE,
        date_from: date | None = None,
        date_to: date | None = None,
        city_ids: list[UUID] | None = None,
        cover_file_id: UUID | None = None,
        city_id: UUID | None = None,  # backward compatibility (visit-v1)
        trip_date: date | None = None,  # backward compatibility (visit-v1)
    ) -> dict[str, Any]:
        resolved_title = self._normalize_title(title)
        resolved_visibility = self._normalize_visibility(visibility)
        resolved_date_from = self._resolve_date_from(date_from=date_from, trip_date=trip_date)
        resolved_trip_date = self._resolve_trip_date(date_from=resolved_date_from, trip_date=trip_date)
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
                cover_file_id=None,
                trip_date=resolved_trip_date,
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
                created = await self.visits_repository.update_by_id(
                    entity_id=created['id'],
                    cover_file_id=cover_file_id,
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
        has_date_from = 'date_from' in payload
        has_trip_date = 'trip_date' in payload
        has_cover_file_id = 'cover_file_id' in payload

        update_payload = dict(payload)
        provided_city_ids = update_payload.pop('city_ids', None)
        provided_city_id = update_payload.pop('city_id', None)
        provided_date_from = update_payload.pop('date_from', None)
        provided_trip_date = update_payload.pop('trip_date', None)

        next_city_ids: list[UUID] | None = None
        if has_city_ids or has_city_id:
            next_city_ids = self._resolve_city_ids(
                city_ids=provided_city_ids if has_city_ids else None,
                city_id=provided_city_id if has_city_id else None,
            )
            update_payload['city_id'] = self._resolve_primary_city_id(next_city_ids)

        if has_date_from or has_trip_date:
            normalized_date_from = provided_date_from if has_date_from else provided_trip_date
            if normalized_date_from is None:
                raise ServiceError('date_from cannot be empty')

            update_payload['date_from'] = normalized_date_from
            update_payload['trip_date'] = provided_trip_date if has_trip_date else normalized_date_from

        if 'title' in update_payload:
            update_payload['title'] = self._normalize_title(update_payload['title'])
        if 'visibility' in update_payload:
            update_payload['visibility'] = self._normalize_visibility(update_payload['visibility'])

        if has_cover_file_id:
            cover_file_id = update_payload.get('cover_file_id')
            if cover_file_id is not None:
                await self._ensure_cover_file_attached(
                    cover_file_id=cover_file_id,
                    visit_id=visit_id,
                    user_id=user_id,
                )

        resulting_date_from = update_payload.get('date_from') or existing.get('date_from') or existing.get('trip_date')
        if resulting_date_from is None:
            raise ServiceError('date_from cannot be empty')
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

        return await self._enrich_visit(updated)

    async def delete_visit_by_id(self, visit_id: UUID, user_id: UUID) -> None:
        await self._get_visit_or_raise(visit_id=visit_id, user_id=user_id)
        await self.visits_repository.delete_by_id(entity_id=visit_id)
