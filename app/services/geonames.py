from __future__ import annotations

import asyncio
import json
import logging
import unicodedata
import urllib.parse
import urllib.request
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

logger = logging.getLogger(__name__)


class GeoNamesClient:
    def __init__(
        self,
        username: str | None,
        base_url: str,
        timeout_seconds: float,
    ):
        self.username = username.strip() if username else None
        self.base_url = base_url.rstrip('/')
        self.timeout_seconds = timeout_seconds

    async def search_countries(self, *, filters: dict[str, Any], limit: int, offset: int) -> list[dict[str, Any]]:
        if not self.username:
            return []

        country_codes = self._extract_country_codes(filters, keys=('iso_a2', 'iso_a2_in'))
        if country_codes:
            rows: list[dict[str, Any]] = []
            for code in country_codes:
                payload = await self._request_json(
                    path='countryInfoJSON',
                    params={'country': code},
                )
                rows.extend(payload.get('geonames', []))
            return self._normalize_countries(rows)

        query = self._extract_query(filters, keys=('name', 'name_ilike', 'name_like'))
        if not query:
            return []

        payload = await self._request_json(
            path='searchJSON',
            params={
                'q': query,
                'featureCode': 'PCLI',
                'maxRows': max(1, min(limit, 100)),
                'startRow': max(offset, 0),
                'style': 'FULL',
            },
        )
        return self._normalize_countries(payload.get('geonames', []))

    async def search_cities(self, *, filters: dict[str, Any], limit: int, offset: int) -> list[dict[str, Any]]:
        if not self.username:
            return []

        query = self._extract_query(
            filters,
            keys=(
                'name',
                'name_ilike',
                'name_like',
                'name_normalized',
                'name_normalized_ilike',
                'name_normalized_like',
            ),
        )
        country_code = self._extract_country_code(filters)

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

        payload = await self._request_json(path='searchJSON', params=params)
        return self._normalize_cities(payload.get('geonames', []))

    async def _request_json(self, *, path: str, params: dict[str, Any]) -> dict[str, Any]:
        if not self.username:
            return {}

        query = urllib.parse.urlencode({'username': self.username, **params})
        url = f'{self.base_url}/{path}?{query}'

        def _load() -> dict[str, Any]:
            with urllib.request.urlopen(url, timeout=self.timeout_seconds) as response:  # noqa: S310
                payload = response.read().decode('utf-8')
                data = json.loads(payload)
                if not isinstance(data, dict):
                    return {}
                return data

        try:
            return await asyncio.to_thread(_load)
        except Exception as exc:  # noqa: BLE001
            logger.warning('GeoNames request failed: %s', exc)
            return {}

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
            if isinstance(value, list):
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
        country_codes = self._extract_country_codes(filters, keys=('country_code', 'country_code_in'))
        return country_codes[0] if country_codes else None

    def _normalize_countries(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        deduplicated: dict[str, dict[str, Any]] = {}
        for row in rows:
            if not isinstance(row, dict):
                continue

            iso_a2 = str(row.get('countryCode', '')).upper().strip()
            name = str(row.get('countryName') or row.get('name') or '').strip()
            if len(iso_a2) != 2 or not name:
                continue

            deduplicated[iso_a2] = {
                'iso_a2': iso_a2,
                'name': name,
                'meta': row,
            }

        return list(deduplicated.values())

    def _normalize_cities(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        deduplicated: dict[UUID, dict[str, Any]] = {}
        for row in rows:
            if not isinstance(row, dict):
                continue

            geoname_id = self._parse_int(row.get('geonameId'))
            country_code = str(row.get('countryCode', '')).upper().strip()
            name = str(row.get('name', '')).strip()
            if geoname_id is None or len(country_code) != 2 or not name:
                continue

            city_id = uuid5(NAMESPACE_URL, f'geonames:city:{geoname_id}')

            deduplicated[city_id] = {
                'id': city_id,
                'country_code': country_code,
                'name': name,
                'name_normalized': self._normalize_text(name),
                'latitude': self._parse_decimal(row.get('lat')),
                'longitude': self._parse_decimal(row.get('lng')),
                'population': self._parse_int(row.get('population')),
                'meta': row,
            }

        return list(deduplicated.values())

    def _normalize_text(self, value: str) -> str:
        normalized = unicodedata.normalize('NFKD', value)
        without_diacritics = ''.join(char for char in normalized if not unicodedata.combining(char))
        return ' '.join(without_diacritics.casefold().split())

    def _parse_decimal(self, value: Any) -> Decimal | None:
        if value is None or value == '':
            return None
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return None

    def _parse_int(self, value: Any) -> int | None:
        if value is None or value == '':
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
