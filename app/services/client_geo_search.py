import json
from typing import Any
from uuid import UUID

from app.repositories.base import PaginatedResponse
from app.repositories.cities import CitiesRepository
from app.repositories.countries import CountriesRepository
from app.services.geonames import GeoNamesClient

SUPPORTED_LANGS = {'en', 'ru'}
NAME_LABEL_FILTERS = {'name', 'name_like', 'name_ilike'}


class ClientGeoSearchService:
    def __init__(
        self,
        countries_repository: CountriesRepository,
        cities_repository: CitiesRepository,
        geonames_client: GeoNamesClient,
    ):
        self.countries_repository = countries_repository
        self.cities_repository = cities_repository
        self.geonames_client = geonames_client

    async def search_countries(
        self,
        limit: int,
        offset: int,
        lang: str | None = None,
        **filters: Any,
    ) -> PaginatedResponse:
        normalized_lang = self._normalize_lang(lang)
        local = await self._search_local_countries(limit=limit, offset=offset, lang=normalized_lang, filters=filters)
        if local.pagination.total > 0:
            return local

        geonames_rows = await self.geonames_client.search_countries(
            query=self._extract_query(filters, keys=('name', 'name_ilike', 'name_like')),
            country_codes=self._extract_country_codes(filters, keys=('iso_a2', 'iso_a2_in')),
            limit=limit,
            offset=offset,
            lang=normalized_lang,
        )
        await self._upsert_countries(geonames_rows)

        return await self._search_local_countries(limit=limit, offset=offset, lang=normalized_lang, filters=filters)

    async def search_cities(
        self,
        limit: int,
        offset: int,
        lang: str | None = None,
        **filters: Any,
    ) -> PaginatedResponse:
        normalized_lang = self._normalize_lang(lang)
        local = await self._search_local_cities(limit=limit, offset=offset, lang=normalized_lang, filters=filters)
        if local.pagination.total > 0:
            return local

        geonames_rows = await self.geonames_client.search_cities(
            query=self._extract_query(
                filters,
                keys=(
                    'name',
                    'name_ilike',
                    'name_like',
                ),
            ),
            country_code=self._extract_country_code(filters),
            limit=limit,
            offset=offset,
            lang=normalized_lang,
        )
        if geonames_rows:
            await self._upsert_countries(self._countries_from_cities(geonames_rows, lang=normalized_lang))
            await self._upsert_cities(geonames_rows)

        return await self._search_local_cities(limit=limit, offset=offset, lang=normalized_lang, filters=filters)

    async def _search_local_countries(
        self,
        *,
        limit: int,
        offset: int,
        lang: str,
        filters: dict[str, Any],
    ) -> PaginatedResponse:
        name_filter = self._extract_name_label_filter(filters)
        if name_filter:
            filter_name, filter_value = name_filter
            response = await self.countries_repository.paginated_search_by_name_or_label(
                lang=lang,
                name_filter_name=filter_name,
                name_filter_value=filter_value,
                order_by='iso_a2',
                limit=limit,
                offset=offset,
                **self._without_filters(filters, NAME_LABEL_FILTERS),
            )
        else:
            response = await self.countries_repository.paginated_search(
                order_by='iso_a2',
                limit=limit,
                offset=offset,
                **filters,
            )

        return self._with_display_names(response, lang=lang)

    async def _search_local_cities(
        self,
        *,
        limit: int,
        offset: int,
        lang: str,
        filters: dict[str, Any],
    ) -> PaginatedResponse:
        name_filter = self._extract_name_label_filter(filters)
        if name_filter:
            filter_name, filter_value = name_filter
            response = await self.cities_repository.paginated_search_by_name_or_label(
                lang=lang,
                name_filter_name=filter_name,
                name_filter_value=filter_value,
                order_by='country_code,name,-population',
                limit=limit,
                offset=offset,
                **self._without_filters(filters, NAME_LABEL_FILTERS),
            )
        else:
            response = await self.cities_repository.paginated_search(
                order_by='country_code,name',
                limit=limit,
                offset=offset,
                **filters,
            )

        return self._with_display_names(response, lang=lang)

    def _countries_from_cities(self, city_rows: list[dict[str, Any]], *, lang: str) -> list[dict[str, Any]]:
        countries: dict[str, dict[str, Any]] = {}
        for row in city_rows:
            country_code = str(row.get('country_code', '')).upper().strip()
            meta = row.get('meta') if isinstance(row.get('meta'), dict) else {}
            country_name = str(meta.get('countryName') or country_code).strip()
            if len(country_code) != 2 or not country_name:
                continue

            countries[country_code] = {
                'iso_a2': country_code,
                'name': country_name,
                'labels': {lang: country_name} if country_name else None,
                'meta': {'countryCode': country_code, 'countryName': country_name, 'source': 'geonames-city-search'},
            }

        return list(countries.values())

    async def _upsert_countries(self, payload: list[dict[str, Any]]) -> int:
        if not payload:
            return 0

        deduplicated: dict[str, dict[str, Any]] = {}
        for item in payload:
            iso_a2 = str(item.get('iso_a2', '')).upper().strip()
            name = str(item.get('name', '')).strip()
            if len(iso_a2) != 2 or not name:
                continue
            deduplicated[iso_a2] = {
                'name': name,
                'meta': item.get('meta'),
                'labels': item.get('labels'),
            }

        if not deduplicated:
            return 0

        country_codes = list(deduplicated.keys())

        async with self.countries_repository.transaction():
            existing_rows = await self.countries_repository.search(iso_a2_in=country_codes)
            existing_by_code = {row['iso_a2']: row for row in existing_rows}
            existing_codes = set(existing_by_code)
            to_insert = [
                {
                    'iso_a2': iso_a2,
                    'name': country_payload['name'],
                    'meta': self._serialize_json_field(country_payload.get('meta')),
                    'labels': self._serialize_json_field(country_payload.get('labels')),
                }
                for iso_a2, country_payload in deduplicated.items()
                if iso_a2 not in existing_codes
            ]
            updated = 0
            for iso_a2, country_payload in deduplicated.items():
                existing = existing_by_code.get(iso_a2)
                if not existing:
                    continue

                update_payload = {
                    'meta': self._serialize_json_field(
                        self._merge_json_objects(existing.get('meta'), country_payload.get('meta'))
                    ),
                    'labels': self._serialize_json_field(
                        self._merge_json_objects(existing.get('labels'), country_payload.get('labels'))
                    ),
                }
                if self._should_replace_country_name(existing.get('name'), iso_a2=iso_a2):
                    update_payload['name'] = country_payload['name']

                await self.countries_repository.update(
                    update_payload,
                    iso_a2=iso_a2,
                )
                updated += 1

            if not to_insert:
                return updated

            await self.countries_repository.create_many(to_insert)
            return len(to_insert) + updated

    async def _upsert_cities(self, payload: list[dict[str, Any]]) -> int:
        if not payload:
            return 0

        deduplicated: dict[UUID, dict[str, Any]] = {}
        for item in payload:
            city_id = item.get('id')
            if not isinstance(city_id, UUID):
                continue
            country_code = str(item.get('country_code', '')).upper().strip()
            name = str(item.get('name', '')).strip()
            if len(country_code) != 2 or not name:
                continue
            deduplicated[city_id] = {
                'country_code': country_code,
                'name': name,
                'latitude': item.get('latitude'),
                'longitude': item.get('longitude'),
                'population': item.get('population'),
                'labels': item.get('labels'),
                'meta': item.get('meta'),
            }

        if not deduplicated:
            return 0

        updated = 0
        inserted = 0
        city_ids = list(deduplicated.keys())

        async with self.cities_repository.transaction():
            existing_rows = await self.cities_repository.search(id_in=city_ids)
            existing_by_id = {row['id']: row for row in existing_rows}
            existing_ids = set(existing_by_id)

            for city_id, city_payload in deduplicated.items():
                if city_id in existing_ids:
                    existing = existing_by_id[city_id]
                    db_payload = {
                        'labels': self._serialize_json_field(
                            self._merge_json_objects(existing.get('labels'), city_payload.get('labels'))
                        ),
                        'meta': self._serialize_json_field(
                            self._merge_json_objects(existing.get('meta'), city_payload.get('meta'))
                        ),
                    }
                    await self.cities_repository.update(db_payload, id=city_id)
                    updated += 1
                else:
                    db_payload = {
                        'country_code': city_payload['country_code'],
                        'name': city_payload['name'],
                        'latitude': city_payload.get('latitude'),
                        'longitude': city_payload.get('longitude'),
                        'population': city_payload.get('population'),
                        'labels': self._serialize_json_field(city_payload.get('labels')),
                        'meta': self._serialize_json_field(city_payload.get('meta')),
                    }
                    await self.cities_repository.create(id=city_id, **db_payload)
                    inserted += 1

        return inserted + updated

    def _normalize_lang(self, value: str | None) -> str:
        if not isinstance(value, str):
            return 'en'
        lang = value.strip().casefold().split('-', maxsplit=1)[0]
        return lang if lang in SUPPORTED_LANGS else 'en'

    def _extract_name_label_filter(self, filters: dict[str, Any]) -> tuple[str, str] | None:
        for key in ('name_ilike', 'name_like', 'name'):
            value = filters.get(key)
            if isinstance(value, str) and value.strip():
                return key, value
        return None

    def _without_filters(self, filters: dict[str, Any], excluded: set[str]) -> dict[str, Any]:
        return {key: value for key, value in filters.items() if key not in excluded}

    def _with_display_names(self, response: PaginatedResponse, *, lang: str) -> PaginatedResponse:
        items = []
        for item in response.items:
            normalized = dict(item)
            normalized['display_name'] = self._display_name(normalized, lang=lang)
            items.append(normalized)
        return PaginatedResponse(items=items, pagination=response.pagination)

    def _display_name(self, row: dict[str, Any], *, lang: str) -> str:
        labels = row.get('labels')
        if isinstance(labels, dict):
            label = labels.get(lang)
            if isinstance(label, str) and label.strip():
                return label.strip()
        return str(row.get('name') or '').strip()

    def _merge_json_objects(self, current: Any, incoming: Any) -> dict[str, Any] | None:
        current_dict = current if isinstance(current, dict) else {}
        incoming_dict = incoming if isinstance(incoming, dict) else {}
        merged = {**current_dict, **incoming_dict}
        return merged or None

    def _should_replace_country_name(self, current_name: Any, *, iso_a2: str) -> bool:
        if not isinstance(current_name, str):
            return True
        normalized = current_name.strip()
        return not normalized or normalized.upper() == iso_a2

    def _extract_query(self, filters: dict[str, Any], keys: tuple[str, ...]) -> str | None:
        for key in keys:
            value = filters.get(key)
            if not isinstance(value, str):
                continue
            cleaned = value.replace('%', ' ').replace('_', ' ').strip()
            if cleaned:
                return cleaned
        return None

    def _extract_country_codes(self, filters: dict[str, Any], keys: tuple[str, ...]) -> list[str]:
        codes: list[str] = []
        for key in keys:
            value = filters.get(key)
            if isinstance(value, str):
                code = value.upper().strip()
                if len(code) == 2:
                    codes.append(code)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        code = item.upper().strip()
                        if len(code) == 2:
                            codes.append(code)

        deduplicated: list[str] = []
        seen: set[str] = set()
        for code in codes:
            if code in seen:
                continue
            deduplicated.append(code)
            seen.add(code)
        return deduplicated

    def _extract_country_code(self, filters: dict[str, Any]) -> str | None:
        codes = self._extract_country_codes(filters, keys=('country_code', 'country_code_in'))
        return codes[0] if codes else None

    def _serialize_json_field(self, value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return json.dumps(value)
