from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


@dataclass(eq=False)
class BaseListRequest:
    limit: int = field(default=100)
    offset: int = field(default=0)

    def to_repo_filters(self) -> dict[str, Any]:
        return {name: value for name, value in vars(self).items() if value is not None}


@dataclass(eq=False)
class CountriesListRequest(BaseListRequest):
    iso_a2: str | None = field(default=None)
    iso_a2_ne: str | None = field(default=None)
    iso_a2_in: list[str] | None = field(default=None)
    iso_a2_notin: list[str] | None = field(default=None)
    iso_a2_like: str | None = field(default=None)
    iso_a2_ilike: str | None = field(default=None)

    name: str | None = field(default=None)
    name_ne: str | None = field(default=None)
    name_in: list[str] | None = field(default=None)
    name_notin: list[str] | None = field(default=None)
    name_like: str | None = field(default=None)
    name_ilike: str | None = field(default=None)

    created: datetime | None = field(default=None)
    created_ne: datetime | None = field(default=None)
    created_lt: datetime | None = field(default=None)
    created_le: datetime | None = field(default=None)
    created_gt: datetime | None = field(default=None)
    created_ge: datetime | None = field(default=None)
    created_in: list[datetime] | None = field(default=None)
    created_notin: list[datetime] | None = field(default=None)

    updated: datetime | None = field(default=None)
    updated_ne: datetime | None = field(default=None)
    updated_lt: datetime | None = field(default=None)
    updated_le: datetime | None = field(default=None)
    updated_gt: datetime | None = field(default=None)
    updated_ge: datetime | None = field(default=None)
    updated_in: list[datetime] | None = field(default=None)
    updated_notin: list[datetime] | None = field(default=None)


def _normalize_client_geo_lang(value: str | None) -> str:
    if not isinstance(value, str):
        return 'en'
    lang = value.strip().casefold().split('-', maxsplit=1)[0]
    return lang if lang in {'en', 'ru'} else 'en'


@dataclass(eq=False)
class ClientGeoCountriesListRequest(CountriesListRequest):
    lang: str | None = field(default=None)

    def to_repo_filters(self) -> dict[str, Any]:
        filters = super().to_repo_filters()
        filters.pop('lang', None)
        return filters

    @property
    def normalized_lang(self) -> str:
        return _normalize_client_geo_lang(self.lang)


@dataclass(eq=False)
class CitiesListRequest(BaseListRequest):
    id: UUID | None = field(default=None)
    id_ne: UUID | None = field(default=None)
    id_in: list[UUID] | None = field(default=None)
    id_notin: list[UUID] | None = field(default=None)

    country_code: str | None = field(default=None)
    country_code_ne: str | None = field(default=None)
    country_code_in: list[str] | None = field(default=None)
    country_code_notin: list[str] | None = field(default=None)
    country_code_like: str | None = field(default=None)
    country_code_ilike: str | None = field(default=None)

    name: str | None = field(default=None)
    name_ne: str | None = field(default=None)
    name_in: list[str] | None = field(default=None)
    name_notin: list[str] | None = field(default=None)
    name_like: str | None = field(default=None)
    name_ilike: str | None = field(default=None)

    latitude: float | None = field(default=None)
    latitude_ne: float | None = field(default=None)
    latitude_lt: float | None = field(default=None)
    latitude_le: float | None = field(default=None)
    latitude_gt: float | None = field(default=None)
    latitude_ge: float | None = field(default=None)
    latitude_in: list[float] | None = field(default=None)
    latitude_notin: list[float] | None = field(default=None)

    longitude: float | None = field(default=None)
    longitude_ne: float | None = field(default=None)
    longitude_lt: float | None = field(default=None)
    longitude_le: float | None = field(default=None)
    longitude_gt: float | None = field(default=None)
    longitude_ge: float | None = field(default=None)
    longitude_in: list[float] | None = field(default=None)
    longitude_notin: list[float] | None = field(default=None)

    population: int | None = field(default=None)
    population_ne: int | None = field(default=None)
    population_lt: int | None = field(default=None)
    population_le: int | None = field(default=None)
    population_gt: int | None = field(default=None)
    population_ge: int | None = field(default=None)
    population_in: list[int] | None = field(default=None)
    population_notin: list[int] | None = field(default=None)

    created: datetime | None = field(default=None)
    created_ne: datetime | None = field(default=None)
    created_lt: datetime | None = field(default=None)
    created_le: datetime | None = field(default=None)
    created_gt: datetime | None = field(default=None)
    created_ge: datetime | None = field(default=None)
    created_in: list[datetime] | None = field(default=None)
    created_notin: list[datetime] | None = field(default=None)

    updated: datetime | None = field(default=None)
    updated_ne: datetime | None = field(default=None)
    updated_lt: datetime | None = field(default=None)
    updated_le: datetime | None = field(default=None)
    updated_gt: datetime | None = field(default=None)
    updated_ge: datetime | None = field(default=None)
    updated_in: list[datetime] | None = field(default=None)
    updated_notin: list[datetime] | None = field(default=None)


@dataclass(eq=False)
class ClientGeoCitiesListRequest(CitiesListRequest):
    lang: str | None = field(default=None)

    def to_repo_filters(self) -> dict[str, Any]:
        filters = super().to_repo_filters()
        filters.pop('lang', None)
        return filters

    @property
    def normalized_lang(self) -> str:
        return _normalize_client_geo_lang(self.lang)


class PaginationResponse(BaseModel):
    limit: int | None
    offset: int
    total: int


class CountryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    iso_a2: str
    name: str
    labels: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None
    created: datetime
    updated: datetime


class ClientGeoCountryResponse(CountryResponse):
    display_name: str


class ClientGeoCountriesListResponse(BaseModel):
    items: list[ClientGeoCountryResponse]
    pagination: PaginationResponse


class CityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    country_code: str
    name: str
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    population: int | None = None
    labels: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None
    created: datetime
    updated: datetime


class ClientGeoCityResponse(CityResponse):
    display_name: str


class ClientGeoCitiesListResponse(BaseModel):
    items: list[ClientGeoCityResponse]
    pagination: PaginationResponse
