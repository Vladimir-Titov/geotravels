from __future__ import annotations

from typing import Any

from app.repositories.countries import CountriesRepository
from helpers.geo import load_geojson
from settings import AppSettings


class CountriesService:
    def __init__(
        self,
        countries_repository: CountriesRepository,
        settings: AppSettings,
    ):
        self.countries_repository = countries_repository
        self.settings = settings

    async def list_countries(self) -> list[dict[str, Any]]:
        return await self.countries_repository.list_all()

    def get_geojson(self) -> dict[str, Any]:
        return load_geojson(str(self.settings.countries_geojson_path))
