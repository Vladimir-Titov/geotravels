from dataclasses import dataclass, field
from typing import Any, Iterable, Literal, Self

from app.services.geoapify.categories import GeoApifyPlaceCategory

JsonObject = dict[str, Any]
GeoApifyPlaceCategoryValue = str | GeoApifyPlaceCategory


def _normalize_values(
    values: Iterable[GeoApifyPlaceCategoryValue] | GeoApifyPlaceCategoryValue | None,
) -> tuple[str, ...]:
    if values is None:
        return ()
    if isinstance(values, str):
        return tuple(value.strip() for value in values.split(',') if value.strip())

    return tuple(str(value).strip() for value in values if str(value).strip())


def _stringify_number(value: float | int) -> str:
    return str(int(value)) if isinstance(value, float) and value.is_integer() else str(value)


@dataclass(frozen=True, slots=True)
class GeoApifyPlaceCircleFilter:
    lon: float
    lat: float
    radius_meters: int

    def __str__(self) -> str:
        return (
            f'circle:{_stringify_number(self.lon)},'
            f'{_stringify_number(self.lat)},'
            f'{_stringify_number(self.radius_meters)}'
        )


@dataclass(frozen=True, slots=True)
class GeoApifyPlaceRectFilter:
    lon1: float
    lat1: float
    lon2: float
    lat2: float

    def __str__(self) -> str:
        return (
            f'rect:{_stringify_number(self.lon1)},'
            f'{_stringify_number(self.lat1)},'
            f'{_stringify_number(self.lon2)},'
            f'{_stringify_number(self.lat2)}'
        )


@dataclass(frozen=True, slots=True)
class GeoApifyPlaceGeometryFilter:
    geometry_id: str

    def __str__(self) -> str:
        return f'geometry:{self.geometry_id}'


@dataclass(frozen=True, slots=True)
class GeoApifyPlaceBoundaryFilter:
    place_id: str

    def __str__(self) -> str:
        return f'place:{self.place_id}'


@dataclass(frozen=True, slots=True)
class GeoApifyPlaceCountryFilter:
    country_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, 'country_codes', _normalize_values(self.country_codes))

    def __str__(self) -> str:
        return f'countrycode:{",".join(self.country_codes)}'


@dataclass(frozen=True, slots=True)
class GeoApifyPlaceProximityBias:
    lon: float
    lat: float

    def __str__(self) -> str:
        return f'proximity:{_stringify_number(self.lon)},{_stringify_number(self.lat)}'


GeoApifyPlaceFilter = (
    GeoApifyPlaceCircleFilter
    | GeoApifyPlaceRectFilter
    | GeoApifyPlaceGeometryFilter
    | GeoApifyPlaceBoundaryFilter
    | GeoApifyPlaceCountryFilter
)
GeoApifyPlaceBias = GeoApifyPlaceProximityBias | GeoApifyPlaceCircleFilter | GeoApifyPlaceRectFilter


@dataclass(frozen=True, slots=True)
class GeoApifyPlaceRequest:
    categories: tuple[GeoApifyPlaceCategoryValue, ...]
    filter: GeoApifyPlaceFilter | str | None = None
    bias: GeoApifyPlaceBias | str | None = None
    conditions: tuple[str, ...] = ()
    limit: int | None = None
    offset: int | None = None
    lang: str | None = None
    name: str | None = None
    api_key: str | None = None

    def __post_init__(self) -> None:
        categories = _normalize_values(self.categories)
        if not categories:
            raise ValueError('GeoApifyPlaceRequest.categories must not be empty')

        object.__setattr__(self, 'categories', categories)
        object.__setattr__(self, 'conditions', _normalize_values(self.conditions))

    def to_query_params(self, *, api_key: str | None = None) -> dict[str, str | int]:
        params: dict[str, str | int] = {
            'categories': ','.join(self.categories),
        }

        if self.conditions:
            params['conditions'] = ','.join(self.conditions)
        if self.filter is not None:
            params['filter'] = str(self.filter)
        if self.bias is not None:
            params['bias'] = str(self.bias)
        if self.limit is not None:
            params['limit'] = self.limit
        if self.offset is not None:
            params['offset'] = self.offset
        if self.lang is not None:
            params['lang'] = self.lang
        if self.name is not None:
            params['name'] = self.name

        resolved_api_key = api_key or self.api_key
        if resolved_api_key is not None:
            params['apiKey'] = resolved_api_key

        return params


@dataclass(frozen=True, slots=True)
class GeoApifyPlaceGeometry:
    type: Literal['Point'] | str
    coordinates: tuple[float, float]

    @property
    def lon(self) -> float:
        return self.coordinates[0]

    @property
    def lat(self) -> float:
        return self.coordinates[1]

    @classmethod
    def from_dict(cls, data: JsonObject) -> Self:
        coordinates = data.get('coordinates', ())
        if not isinstance(coordinates, Iterable):
            coordinates = ()

        lon, lat = tuple(coordinates)[:2]
        return cls(
            type=str(data.get('type', 'Point')),
            coordinates=(float(lon), float(lat)),
        )

    def to_dict(self) -> JsonObject:
        return {
            'type': self.type,
            'coordinates': list(self.coordinates),
        }


@dataclass(frozen=True, slots=True)
class GeoApifyPlaceProperties:
    name: str | None = None
    country: str | None = None
    country_code: str | None = None
    state: str | None = None
    county: str | None = None
    city: str | None = None
    district: str | None = None
    suburb: str | None = None
    postcode: str | None = None
    street: str | None = None
    housenumber: str | None = None
    lat: float | None = None
    lon: float | None = None
    formatted: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    address_line3: str | None = None
    categories: tuple[str, ...] = ()
    details: tuple[str, ...] = ()
    datasource: JsonObject | None = None
    website: str | None = None
    opening_hours: str | None = None
    contact: JsonObject | None = None
    facilities: JsonObject | None = None
    wiki_and_media: JsonObject | None = None
    brand: str | None = None
    operator: str | None = None
    distance: float | None = None
    place_id: str | None = None
    extra: JsonObject = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: JsonObject) -> Self:
        known_fields = {
            'name',
            'country',
            'country_code',
            'state',
            'county',
            'city',
            'district',
            'suburb',
            'postcode',
            'street',
            'housenumber',
            'lat',
            'lon',
            'formatted',
            'address_line1',
            'address_line2',
            'address_line3',
            'categories',
            'details',
            'datasource',
            'website',
            'opening_hours',
            'contact',
            'facilities',
            'wiki_and_media',
            'brand',
            'operator',
            'distance',
            'place_id',
        }
        extra = {key: value for key, value in data.items() if key not in known_fields}

        return cls(
            name=data.get('name'),
            country=data.get('country'),
            country_code=data.get('country_code'),
            state=data.get('state'),
            county=data.get('county'),
            city=data.get('city'),
            district=data.get('district'),
            suburb=data.get('suburb'),
            postcode=data.get('postcode'),
            street=data.get('street'),
            housenumber=data.get('housenumber'),
            lat=_optional_float(data.get('lat')),
            lon=_optional_float(data.get('lon')),
            formatted=data.get('formatted'),
            address_line1=data.get('address_line1'),
            address_line2=data.get('address_line2'),
            address_line3=data.get('address_line3'),
            categories=_normalize_values(data.get('categories')),
            details=_normalize_values(data.get('details')),
            datasource=_optional_object(data.get('datasource')),
            website=data.get('website'),
            opening_hours=data.get('opening_hours'),
            contact=_optional_object(data.get('contact')),
            facilities=_optional_object(data.get('facilities')),
            wiki_and_media=_optional_object(data.get('wiki_and_media')),
            brand=data.get('brand'),
            operator=data.get('operator'),
            distance=_optional_float(data.get('distance')),
            place_id=data.get('place_id'),
            extra=extra,
        )

    def to_dict(self) -> JsonObject:
        data = {
            'name': self.name,
            'country': self.country,
            'country_code': self.country_code,
            'state': self.state,
            'county': self.county,
            'city': self.city,
            'district': self.district,
            'suburb': self.suburb,
            'postcode': self.postcode,
            'street': self.street,
            'housenumber': self.housenumber,
            'lat': self.lat,
            'lon': self.lon,
            'formatted': self.formatted,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'address_line3': self.address_line3,
            'categories': list(self.categories),
            'details': list(self.details),
            'datasource': self.datasource,
            'website': self.website,
            'opening_hours': self.opening_hours,
            'contact': self.contact,
            'facilities': self.facilities,
            'wiki_and_media': self.wiki_and_media,
            'brand': self.brand,
            'operator': self.operator,
            'distance': self.distance,
            'place_id': self.place_id,
            **self.extra,
        }
        return {key: value for key, value in data.items() if value not in (None, [], {})}


@dataclass(frozen=True, slots=True)
class GeoApifyPlaceFeature:
    properties: GeoApifyPlaceProperties
    geometry: GeoApifyPlaceGeometry
    type: Literal['Feature'] | str = 'Feature'
    bbox: tuple[float, ...] | None = None
    extra: JsonObject = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: JsonObject) -> Self:
        known_fields = {'type', 'properties', 'geometry', 'bbox'}
        extra = {key: value for key, value in data.items() if key not in known_fields}
        bbox = data.get('bbox')

        return cls(
            type=str(data.get('type', 'Feature')),
            properties=GeoApifyPlaceProperties.from_dict(_optional_object(data.get('properties')) or {}),
            geometry=GeoApifyPlaceGeometry.from_dict(_optional_object(data.get('geometry')) or {}),
            bbox=tuple(float(value) for value in bbox) if isinstance(bbox, Iterable) else None,
            extra=extra,
        )

    def to_dict(self) -> JsonObject:
        data = {
            'type': self.type,
            'properties': self.properties.to_dict(),
            'geometry': self.geometry.to_dict(),
            'bbox': list(self.bbox) if self.bbox is not None else None,
            **self.extra,
        }
        return {key: value for key, value in data.items() if value is not None}


@dataclass(frozen=True, slots=True)
class GeoApifyPlaceResponse:
    features: tuple[GeoApifyPlaceFeature, ...]
    type: Literal['FeatureCollection'] | str = 'FeatureCollection'
    bbox: tuple[float, ...] | None = None
    extra: JsonObject = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: JsonObject) -> Self:
        known_fields = {'type', 'features', 'bbox'}
        extra = {key: value for key, value in data.items() if key not in known_fields}
        bbox = data.get('bbox')
        features = data.get('features') or ()

        return cls(
            type=str(data.get('type', 'FeatureCollection')),
            features=tuple(
                GeoApifyPlaceFeature.from_dict(feature) for feature in features if isinstance(feature, dict)
            ),
            bbox=tuple(float(value) for value in bbox) if isinstance(bbox, Iterable) else None,
            extra=extra,
        )

    def __iter__(self) -> Iterable[GeoApifyPlaceFeature]:
        return iter(self.features)

    def __len__(self) -> int:
        return len(self.features)

    def to_dict(self) -> JsonObject:
        data = {
            'type': self.type,
            'features': [feature.to_dict() for feature in self.features],
            'bbox': list(self.bbox) if self.bbox is not None else None,
            **self.extra,
        }
        return {key: value for key, value in data.items() if value is not None}


def _optional_float(value: Any) -> float | None:
    return None if value is None else float(value)


def _optional_object(value: Any) -> JsonObject | None:
    return value if isinstance(value, dict) else None
