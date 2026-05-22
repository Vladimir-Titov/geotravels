from math import asin, cos, radians, sin, sqrt
from uuid import UUID

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
DEFAULT_POPULAR_PLACES_RADIUS_METERS = 50_000
EARTH_RADIUS_METERS = 6_371_000


class PlacesService:
    def __init__(
        self,
        geoapify_client: GeoApifyClient,
        cities_repository: CitiesRepository,
    ):
        self.geoapify_client = geoapify_client
        self.cities_repository = cities_repository

    async def suggest_places(self, city_id: UUID) -> list[str]:
        try:
            city = await self.cities_repository.get_by_id(city_id)
        except RowNotFoundError as exc:
            raise NotFoundError('City not found') from exc

        lat, lng = self._get_city_coordinates(city)
        search_request = GeoApifyPlaceRequest(
            categories=POPULAR_PLACE_CATEGORIES,
            conditions=('named',),
            filter=self._get_city_filter(city, lat=lat, lng=lng),
            bias=GeoApifyPlaceProximityBias(lon=lng, lat=lat),
            limit=DEFAULT_POPULAR_PLACES_LIMIT,
        )
        response = await self.geoapify_client.search_places(search_request)
        print(response)

        return self._extract_place_names(response)

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

    def _extract_place_names(self, response) -> list[str]:
        names: list[str] = []
        seen: set[str] = set()

        for feature in response:
            name = feature.properties.name
            if not name:
                continue

            normalized_name = name.strip()
            normalized_key = normalized_name.casefold()
            if not normalized_name or normalized_key in seen:
                continue

            names.append(normalized_name)
            seen.add(normalized_key)

        return names
