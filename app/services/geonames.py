import logging
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

from aiohttp import ClientSession

logger = logging.getLogger(__name__)


class GeoNamesClient:
    def __init__(
        self,
        username: str | None,
        base_url: str,
        timeout_seconds: float,
        session: ClientSession,
    ):
        self.username = username.strip() if username else None
        self.base_url = base_url.rstrip('/')
        self.timeout_seconds = timeout_seconds
        self.session = session

    async def search_countries(
        self,
        *,
        query: str | None,
        country_codes: list[str],
        limit: int,
        offset: int,
        lang: str | None = None,
    ) -> list[dict[str, Any]]:
        if not self.username:
            return []

        if country_codes:
            rows: list[dict[str, Any]] = []
            for code in country_codes:
                payload = await self._request_json(
                    path='countryInfoJSON',
                    params=self._with_lang({'country': code}, lang),
                )
                rows.extend(payload.get('geonames', []))
            return self._normalize_countries(rows, lang=lang)

        if not query:
            return []

        payload = await self._request_json(
            path='searchJSON',
            params=self._with_lang(
                {
                    'q': query,
                    'featureCode': 'PCLI',
                    'maxRows': max(1, min(limit, 100)),
                    'startRow': max(offset, 0),
                    'style': 'FULL',
                },
                lang,
            ),
        )
        return self._normalize_countries(payload.get('geonames', []), lang=lang)

    async def search_cities(
        self,
        *,
        query: str | None,
        country_code: str | None,
        limit: int,
        offset: int,
        lang: str | None = None,
    ) -> list[dict[str, Any]]:
        if not self.username:
            return []

        if not query and not country_code:
            return []
        params: dict[str, Any] = {
            'featureClass': 'P',
            'maxRows': max(1, min(limit, 100)),
            'startRow': max(offset, 0),
            'style': 'FULL',
        }
        if query:
            params['q'] = query
        if country_code:
            params['country'] = country_code

        params = self._with_lang(params, lang)
        payload = await self._request_json(path='searchJSON', params=params)
        return self._normalize_cities(payload.get('geonames', []), lang=lang)

    async def _request_json(self, *, path: str, params: dict[str, Any]) -> dict[str, Any]:
        if not self.username:
            return {}

        try:
            async with self.session.get(
                f'{self.base_url}/{path}',
                params={'username': self.username, **params},
                timeout=self.timeout_seconds,
            ) as response:
                response.raise_for_status()
                payload = await response.json()
                return payload
        except Exception as exc:  # noqa: BLE001
            logger.warning('GeoNames request failed: %s', exc)
            return {}

    def _with_lang(self, params: dict[str, Any], lang: str | None) -> dict[str, Any]:
        if lang:
            return {**params, 'lang': lang}
        return params

    def _normalize_countries(self, rows: list[dict[str, Any]], *, lang: str | None = None) -> list[dict[str, Any]]:
        deduplicated: dict[str, dict[str, Any]] = {}
        for row in rows:
            if not isinstance(row, dict):
                continue

            iso_a2 = str(row.get('countryCode', '')).upper().strip()
            localized_name = self._first_text(row, ('countryName', 'name'))
            name = self._first_text(row, ('toponymName', 'asciiName')) or localized_name
            if len(iso_a2) != 2 or not name:
                continue

            deduplicated[iso_a2] = {
                'iso_a2': iso_a2,
                'name': name,
                'labels': self._build_labels(canonical=name, localized=localized_name, lang=lang),
                'meta': row,
            }

        return list(deduplicated.values())

    def _normalize_cities(self, rows: list[dict[str, Any]], *, lang: str | None = None) -> list[dict[str, Any]]:
        deduplicated: dict[UUID, dict[str, Any]] = {}
        for row in rows:
            if not isinstance(row, dict):
                continue

            geoname_id = self._parse_int(row.get('geonameId'))
            country_code = str(row.get('countryCode', '')).upper().strip()
            localized_name = self._first_text(row, ('name',))
            name = self._first_text(row, ('toponymName', 'asciiName')) or localized_name
            if geoname_id is None or len(country_code) != 2 or not name:
                continue

            city_id = uuid5(NAMESPACE_URL, f'geonames:city:{geoname_id}')

            deduplicated[city_id] = {
                'id': city_id,
                'country_code': country_code,
                'name': name,
                'latitude': self._parse_decimal(row.get('lat')),
                'longitude': self._parse_decimal(row.get('lng')),
                'population': self._parse_int(row.get('population')),
                'labels': self._build_labels(canonical=name, localized=localized_name, lang=lang),
                'meta': row,
            }

        return list(deduplicated.values())

    def _first_text(self, row: dict[str, Any], keys: tuple[str, ...]) -> str:
        for key in keys:
            value = row.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ''

    def _build_labels(self, *, canonical: str, localized: str, lang: str | None) -> dict[str, str]:
        labels = {'en': canonical}
        if lang:
            labels[lang] = localized or canonical
        return labels

    def _parse_decimal(self, value: Any) -> Decimal | None:
        if value is None or value == '':
            return None
        try:
            return Decimal(str(value))
        except InvalidOperation, ValueError:
            return None

    def _parse_int(self, value: Any) -> int | None:
        if value is None or value == '':
            return None
        try:
            return int(value)
        except TypeError, ValueError:
            return None
