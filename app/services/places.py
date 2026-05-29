from math import asin, cos, radians, sin, sqrt
from uuid import UUID

import ujson

from app.repositories import CitiesRepository
from app.repositories.base import RowNotFoundError
from app.services.exceptions import NotFoundError, ServiceError
from app.services.geoapify import GeoApifyPlaceCategory
from app.services.geoapify.client import GeoApifyClient
from app.services.geoapify.schemas import (
    GeoApifyPlaceCircleFilter,
    GeoApifyPlaceProximityBias,
    GeoApifyPlaceRequest,
)
from app.services.llm.deepseek import DeepSeekClient, DeepSeekCompletionRequest
from app.services.llm.prompts import get_suggest_place_prompt

POPULAR_PLACE_CATEGORIES = (
    GeoApifyPlaceCategory.TOURISM_ATTRACTION,
    GeoApifyPlaceCategory.TOURISM_ATTRACTION_VIEWPOINT,
    GeoApifyPlaceCategory.TOURISM_SIGHTS,
    GeoApifyPlaceCategory.ENTERTAINMENT_MUSEUM,
    GeoApifyPlaceCategory.HERITAGE,
    GeoApifyPlaceCategory.HERITAGE_UNESCO,
    GeoApifyPlaceCategory.NATIONAL_PARK,
    GeoApifyPlaceCategory.LEISURE_PARK,
    GeoApifyPlaceCategory.LEISURE_PARK_GARDEN,
    GeoApifyPlaceCategory.LEISURE_PARK_NATURE_RESERVE,
    GeoApifyPlaceCategory.NATURAL_PROTECTED_AREA,
)
DEFAULT_POPULAR_PLACES_LIMIT = 20
GEOAPIFY_POPULAR_PLACES_FETCH_LIMIT = 100
DEFAULT_POPULAR_PLACES_RADIUS_METERS = 50_000
DEFAULT_GEOAPIFY_LANG = 'en'
EARTH_RADIUS_METERS = 6_371_000
PLACE_CATEGORY_SCORES = {
    'heritage.unesco': 120,
    'tourism.sights': 90,
    'tourism.attraction': 80,
    'entertainment.museum': 75,
    'heritage': 70,
    'national_park': 65,
    'tourism.attraction.viewpoint': 60,
    'leisure.park.garden': 50,
    'leisure.park.nature_reserve': 50,
    'natural.protected_area': 45,
    'leisure.park': 40,
}
WIKI_AND_MEDIA_SCORE = 25
WEBSITE_SCORE = 10
DISTANCE_SCORE_PENALTY_PER_KM = 0.7
MAX_DISTANCE_SCORE_PENALTY = 35


class PlacesService:
    def __init__(
        self,
        geoapify_client: GeoApifyClient,
        cities_repository: CitiesRepository,
        deepseek_client: DeepSeekClient,
    ):
        self.geoapify_client = geoapify_client
        self.cities_repository = cities_repository
        self.deepseek_client = deepseek_client

    async def suggest_places(self, city_id: UUID, lang: str = DEFAULT_GEOAPIFY_LANG) -> list[dict[str, str]]:
        try:
            city = await self.cities_repository.get_by_id(city_id)
        except RowNotFoundError as exc:
            raise NotFoundError('City not found') from exc

        normalized_lang = self._normalize_lang(lang)
        lat, lng = self._get_city_coordinates(city)
        search_request = GeoApifyPlaceRequest(
            categories=POPULAR_PLACE_CATEGORIES,
            conditions=('named',),
            filter=self._get_city_filter(city, lat=lat, lng=lng),
            bias=GeoApifyPlaceProximityBias(lon=lng, lat=lat),
            limit=GEOAPIFY_POPULAR_PLACES_FETCH_LIMIT,
            lang=normalized_lang,
        )
        response = await self.geoapify_client.search_places(search_request)

        names = self._extract_place_names(response, lat=lat, lng=lng, lang=normalized_lang)
        completions_request = DeepSeekCompletionRequest(
            model='deepseek-v4-flash',
            prompt=get_suggest_place_prompt(lang=normalized_lang, names=names, city=city),
        )
        completions = await self.deepseek_client.completions(completions_request)
        if not completions.choices:
            raise ServiceError('DeepSeek returned no completion choices')

        resp = completions.choices[0].text
        try:
            return ujson.loads(resp)
        except ValueError as exc:
            raise ServiceError('DeepSeek returned malformed JSON') from exc

    def _normalize_lang(self, value: str | None) -> str:
        if not isinstance(value, str):
            return DEFAULT_GEOAPIFY_LANG

        lang = value.strip().casefold().split('-', maxsplit=1)[0]
        if len(lang) == 2 and lang.isascii() and lang.isalpha():
            return lang

        return DEFAULT_GEOAPIFY_LANG

    def _get_city_filter(
        self,
        city: dict,
        *,
        lat: float,
        lng: float,
    ) -> GeoApifyPlaceCircleFilter:
        radius_meters = max(
            DEFAULT_POPULAR_PLACES_RADIUS_METERS,
            self._get_bbox_radius_meters(city, lat=lat, lng=lng) or 0,
        )
        return GeoApifyPlaceCircleFilter(lon=lng, lat=lat, radius_meters=round(radius_meters))

    def _get_bbox_radius_meters(self, city: dict, *, lat: float, lng: float) -> float | None:
        meta = self._get_city_meta(city)
        bbox = meta.get('bbox') if isinstance(meta.get('bbox'), dict) else {}
        try:
            north = float(bbox['north'])
            east = float(bbox['east'])
            south = float(bbox['south'])
            west = float(bbox['west'])
        except (KeyError, TypeError, ValueError):
            return None

        return max(
            self._distance_meters(lat, lng, north, east),
            self._distance_meters(lat, lng, north, west),
            self._distance_meters(lat, lng, south, east),
            self._distance_meters(lat, lng, south, west),
        )

    def _get_city_coordinates(self, city: dict) -> tuple[float, float]:
        meta = self._get_city_meta(city)
        raw_lat = meta.get('lat') or city.get('latitude')
        raw_lng = meta.get('lng') or city.get('longitude')

        if raw_lat is None or raw_lng is None:
            raise ServiceError('City coordinates not found')

        try:
            return float(raw_lat), float(raw_lng)
        except (TypeError, ValueError) as exc:
            raise ServiceError('City coordinates are invalid') from exc

    def _get_city_meta(self, city: dict) -> dict:
        meta = city.get('meta')
        return meta if isinstance(meta, dict) else {}

    def _distance_meters(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        value = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
        return 2 * EARTH_RADIUS_METERS * asin(sqrt(value))

    def _extract_place_names(self, response, *, lat: float, lng: float, lang: str) -> list[dict[str, str]]:
        scored_by_name: dict[str, tuple[float, float, int, str, str]] = {}

        for index, feature in enumerate(response):
            name = self._get_feature_name(feature, lang=lang)
            if not name:
                continue

            normalized_name = name.strip()
            normalized_key = normalized_name.casefold()
            if not normalized_name:
                continue

            distance_meters = self._get_feature_distance_meters(feature, lat=lat, lng=lng)
            score = self._score_feature(feature, distance_meters=distance_meters)
            sortable = (score, -distance_meters, -index)
            existing = scored_by_name.get(normalized_key)
            if existing is None or sortable > existing[:3]:
                scored_by_name[normalized_key] = (*sortable, normalized_name, self._get_feature_address(feature))

        scored_places = sorted(scored_by_name.values(), reverse=True)
        return [{name: address} for *_score_parts, name, address in scored_places[:DEFAULT_POPULAR_PLACES_LIMIT]]

    def _get_feature_name(self, feature, *, lang: str) -> str | None:
        localized_names = feature.properties.extra.get('name_international')
        if isinstance(localized_names, dict):
            localized_name = localized_names.get(lang)
            if isinstance(localized_name, str) and localized_name.strip():
                return localized_name

        for key in (f'name_{lang}', f'name:{lang}'):
            localized_name = feature.properties.extra.get(key)
            if isinstance(localized_name, str) and localized_name.strip():
                return localized_name

        return feature.properties.name

    def _get_feature_address(self, feature) -> str:
        for value in (
            feature.properties.formatted,
            feature.properties.address_line2,
            feature.properties.address_line3,
        ):
            if isinstance(value, str) and value.strip():
                return value.strip()

        return ''

    def _score_feature(self, feature, *, distance_meters: float) -> float:
        category_score = max(
            (
                score
                for category in feature.properties.categories
                for prefix, score in PLACE_CATEGORY_SCORES.items()
                if category == prefix or category.startswith(f'{prefix}.')
            ),
            default=0,
        )
        metadata_score = 0
        if feature.properties.wiki_and_media:
            metadata_score += WIKI_AND_MEDIA_SCORE
        if feature.properties.website:
            metadata_score += WEBSITE_SCORE

        distance_penalty = min(
            (distance_meters / 1000) * DISTANCE_SCORE_PENALTY_PER_KM,
            MAX_DISTANCE_SCORE_PENALTY,
        )
        return category_score + metadata_score - distance_penalty

    def _get_feature_distance_meters(self, feature, *, lat: float, lng: float) -> float:
        if feature.properties.distance is not None:
            return feature.properties.distance

        return self._distance_meters(
            lat,
            lng,
            feature.geometry.lat,
            feature.geometry.lon,
        )
