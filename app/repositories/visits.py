from datetime import date
from typing import Any
from uuid import UUID, uuid7

from sqlalchemy import and_, exists, func, select

from app.models.tables import (
    CheckListStatus,
    VisitStatus,
    VisitVisibility,
    cities,
    countries,
    files,
    files_visits,
    visits,
    visits_checklist,
    visits_cities,
    visits_places,
)
from app.repositories.base import BaseEntityDBRepository, PaginatedResponse, Pagination


class VisitsRepository(BaseEntityDBRepository):
    entity = visits

    async def create(
        self,
        user_id: UUID,
        country_code: str,
        title: str,
        description: str | None,
        visibility: VisitVisibility,
        date_from: date | None,
        date_to: date | None,
        city_id: UUID | None,
        status: VisitStatus,
    ) -> dict[str, Any]:
        return await super().create(
            id=uuid7(),
            user_id=user_id,
            country_code=country_code,
            title=title,
            description=description,
            visibility=visibility.value,
            date_from=date_from,
            date_to=date_to,
            city_id=city_id,
            status=status.value,
        )

    async def list_by_user(self, user_id: UUID) -> list[dict[str, Any]]:
        return await self.search(user_id=user_id, order_by=['-created', '-id'])

    async def list_unique_country_codes_by_user(self, user_id: UUID) -> list[str]:
        query = (
            select(visits.c.country_code)
            .where(visits.c.user_id == user_id)
            .distinct()
            .order_by(visits.c.country_code.asc())
        )
        rows = await self.fetch(query)
        return [str(row['country_code']) for row in rows]

    def _ranked_visit_files(self, user_id: UUID) -> Any:
        return (
            select(
                files_visits.c.visit_id,
                files_visits.c.file_id,
                func.row_number()
                .over(
                    partition_by=files_visits.c.visit_id,
                    order_by=(files_visits.c.is_cover.desc(), files_visits.c.id.desc()),
                )
                .label('row_num'),
            )
            .where(files_visits.c.user_id == user_id, files_visits.c.file_id.is_not(None))
            .subquery()
        )

    def _photo_counts(self, user_id: UUID) -> Any:
        return (
            select(
                files_visits.c.visit_id,
                func.count(files_visits.c.file_id).label('photos_count'),
            )
            .where(files_visits.c.user_id == user_id, files_visits.c.file_id.is_not(None))
            .group_by(files_visits.c.visit_id)
            .subquery()
        )

    def _checklist_counts(self, user_id: UUID) -> Any:
        return (
            select(
                visits_checklist.c.visit_id,
                func.count(visits_checklist.c.id).label('checklist_total'),
                func.count(visits_checklist.c.id)
                .filter(visits_checklist.c.status == CheckListStatus.DONE.value)
                .label('checklist_done'),
            )
            .where(visits_checklist.c.user_id == user_id)
            .group_by(visits_checklist.c.visit_id)
            .subquery()
        )

    def _places_counts(self, user_id: UUID) -> Any:
        return (
            select(
                visits_places.c.visit_id,
                func.count(visits_places.c.id).label('places_total'),
                func.count(visits_places.c.id).filter(visits_places.c.is_visited.is_(True)).label('places_visited'),
            )
            .where(visits_places.c.user_id == user_id)
            .group_by(visits_places.c.visit_id)
            .subquery()
        )

    async def list_visit_cards(
        self,
        user_id: UUID,
        status: VisitStatus,
        limit: int,
        offset: int,
    ) -> PaginatedResponse:
        status_value = status.value
        ranked_files = self._ranked_visit_files(user_id)
        photo_counts = self._photo_counts(user_id)
        checklist_counts = self._checklist_counts(user_id)
        places_counts = self._places_counts(user_id)

        query = (
            select(
                visits.c.id,
                visits.c.status,
                visits.c.title,
                visits.c.country_code,
                countries.c.name.label('country_name'),
                visits.c.city_id,
                cities.c.name.label('city_name'),
                visits.c.date_from,
                visits.c.date_to,
                ranked_files.c.file_id.label('cover_file_id'),
                func.coalesce(photo_counts.c.photos_count, 0).label('photos_count'),
                func.coalesce(checklist_counts.c.checklist_total, 0).label('checklist_total'),
                func.coalesce(checklist_counts.c.checklist_done, 0).label('checklist_done'),
                func.coalesce(places_counts.c.places_total, 0).label('places_total'),
                func.coalesce(places_counts.c.places_visited, 0).label('places_visited'),
            )
            .select_from(
                visits.join(countries, countries.c.iso_a2 == visits.c.country_code)
                .outerjoin(cities, cities.c.id == visits.c.city_id)
                .outerjoin(
                    ranked_files,
                    and_(ranked_files.c.visit_id == visits.c.id, ranked_files.c.row_num == 1),
                )
                .outerjoin(photo_counts, photo_counts.c.visit_id == visits.c.id)
                .outerjoin(checklist_counts, checklist_counts.c.visit_id == visits.c.id)
                .outerjoin(places_counts, places_counts.c.visit_id == visits.c.id)
            )
            .where(visits.c.user_id == user_id, visits.c.status == status_value)
            .limit(limit)
            .offset(offset)
        )

        if status_value == VisitStatus.PLANNED.value:
            query = query.order_by(visits.c.date_from.asc().nulls_last(), visits.c.created.desc(), visits.c.id.desc())
        else:
            query = query.order_by(visits.c.date_from.desc().nulls_last(), visits.c.created.desc(), visits.c.id.desc())

        count_query = (
            select(func.count()).select_from(visits).where(visits.c.user_id == user_id, visits.c.status == status_value)
        )

        rows = await self.fetch(query)
        total = int(await self.fetchval(count_query) or 0)
        return PaginatedResponse(
            items=[self._normalize_card_row(row) for row in rows],
            pagination=Pagination(limit=limit, offset=offset, total=total),
        )

    async def get_visit_detail_header(self, visit_id: UUID, user_id: UUID) -> dict[str, Any] | None:
        ranked_files = self._ranked_visit_files(user_id)
        query = (
            select(
                visits,
                countries.c.name.label('country_name'),
                cities.c.name.label('city_name'),
                ranked_files.c.file_id.label('cover_file_id'),
            )
            .select_from(
                visits.join(countries, countries.c.iso_a2 == visits.c.country_code)
                .outerjoin(cities, cities.c.id == visits.c.city_id)
                .outerjoin(
                    ranked_files,
                    and_(ranked_files.c.visit_id == visits.c.id, ranked_files.c.row_num == 1),
                )
            )
            .where(visits.c.id == visit_id, visits.c.user_id == user_id)
        )
        row = await self.fetchrow(query)
        return self._normalize_detail_header_row(row) if row else None

    async def list_visit_detail_photos(self, visit_id: UUID, user_id: UUID) -> list[dict[str, Any]]:
        query = (
            select(
                files.c.id,
                files.c.filename,
                files.c.file_type,
                files_visits.c.is_private,
                files_visits.c.is_cover,
                files_visits.c.created,
            )
            .select_from(files_visits.join(files, files.c.id == files_visits.c.file_id))
            .where(
                files_visits.c.visit_id == visit_id,
                files_visits.c.user_id == user_id,
                files_visits.c.file_id.is_not(None),
            )
            .order_by(files_visits.c.is_cover.desc(), files_visits.c.created.asc(), files_visits.c.id.asc())
        )
        rows = await self.fetch(query)
        return [self._normalize_uuid_fields(row, ('id',)) for row in rows]

    async def list_visit_detail_checklist(self, visit_id: UUID, user_id: UUID) -> list[dict[str, Any]]:
        query = (
            select(visits_checklist)
            .where(visits_checklist.c.visit_id == visit_id, visits_checklist.c.user_id == user_id)
            .order_by(visits_checklist.c.created.asc(), visits_checklist.c.id.asc())
        )
        rows = await self.fetch(query)
        return [self._normalize_uuid_fields(row, ('id', 'visit_id', 'user_id')) for row in rows]

    async def list_visit_detail_places(self, visit_id: UUID, user_id: UUID) -> list[dict[str, Any]]:
        query = (
            select(visits_places)
            .where(visits_places.c.visit_id == visit_id, visits_places.c.user_id == user_id)
            .order_by(visits_places.c.created.asc(), visits_places.c.id.asc())
        )
        rows = await self.fetch(query)
        return [self._normalize_uuid_fields(row, ('id', 'visit_id', 'user_id')) for row in rows]

    async def list_visit_detail_cities(self, visit_id: UUID) -> list[dict[str, Any]]:
        query = (
            select(cities.c.id, cities.c.name, cities.c.country_code)
            .select_from(visits_cities.join(cities, cities.c.id == visits_cities.c.city_id))
            .where(visits_cities.c.visit_id == visit_id)
            .order_by(visits_cities.c.created.asc(), visits_cities.c.id.asc())
        )
        rows = await self.fetch(query)
        return [self._normalize_uuid_fields(row, ('id',)) for row in rows]

    async def list_user_visits_for_statistics(self, user_id: UUID) -> list[dict[str, Any]]:
        query = (
            select(
                visits.c.id,
                visits.c.status,
                visits.c.country_code,
                countries.c.name.label('country_name'),
                visits.c.city_id,
                cities.c.name.label('city_name'),
            )
            .select_from(
                visits.join(countries, countries.c.iso_a2 == visits.c.country_code).outerjoin(
                    cities,
                    cities.c.id == visits.c.city_id,
                )
            )
            .where(
                visits.c.user_id == user_id,
                visits.c.status.in_([VisitStatus.VISITED.value, VisitStatus.PLANNED.value]),
            )
        )
        rows = await self.fetch(query)
        return [self._normalize_uuid_fields(row, ('id', 'city_id')) for row in rows]

    async def list_user_visit_city_links_for_statistics(self, user_id: UUID) -> list[dict[str, Any]]:
        has_visit_city = exists().where(visits_cities.c.visit_id == visits.c.id)
        explicit_city_links = (
            select(
                visits.c.id.label('visit_id'),
                cities.c.id.label('city_id'),
                cities.c.name.label('city_name'),
            )
            .select_from(
                visits.join(visits_cities, visits_cities.c.visit_id == visits.c.id).join(
                    cities,
                    cities.c.id == visits_cities.c.city_id,
                )
            )
            .where(visits.c.user_id == user_id, visits.c.status == VisitStatus.VISITED.value)
        )
        fallback_city_links = (
            select(
                visits.c.id.label('visit_id'),
                cities.c.id.label('city_id'),
                cities.c.name.label('city_name'),
            )
            .select_from(visits.join(cities, cities.c.id == visits.c.city_id))
            .where(
                visits.c.user_id == user_id,
                visits.c.status == VisitStatus.VISITED.value,
                visits.c.city_id.is_not(None),
                ~has_visit_city,
            )
        )
        rows = await self.fetch(explicit_city_links.union_all(fallback_city_links))
        return [self._normalize_uuid_fields(row, ('visit_id', 'city_id')) for row in rows]

    def _normalize_row(self, row: dict[str, Any]) -> dict[str, Any]:
        if isinstance(row.get('id'), str):
            row['id'] = UUID(row['id'])
        if isinstance(row.get('user_id'), str):
            row['user_id'] = UUID(row['user_id'])
        if isinstance(row.get('city_id'), str):
            row['city_id'] = UUID(row['city_id'])
        return row

    @staticmethod
    def _normalize_uuid_fields(row: dict[str, Any], field_names: tuple[str, ...]) -> dict[str, Any]:
        normalized = dict(row)
        for field_name in field_names:
            if isinstance(normalized.get(field_name), str):
                normalized[field_name] = UUID(normalized[field_name])
        return normalized

    def _normalize_card_row(self, row: dict[str, Any]) -> dict[str, Any]:
        normalized = self._normalize_uuid_fields(row, ('id', 'city_id', 'cover_file_id'))
        for field_name in ('photos_count', 'checklist_total', 'checklist_done', 'places_total', 'places_visited'):
            normalized[field_name] = int(normalized.get(field_name) or 0)
        return normalized

    def _normalize_detail_header_row(self, row: dict[str, Any]) -> dict[str, Any]:
        return self._normalize_uuid_fields(row, ('id', 'user_id', 'city_id', 'cover_file_id'))
