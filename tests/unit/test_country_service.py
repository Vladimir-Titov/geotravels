from __future__ import annotations

import pytest

from app.repositories.countries import CountriesRepository
from app.services.countries import CountriesService


@pytest.mark.asyncio
async def test_list_countries_and_geojson(db_pool, settings) -> None:
    service = CountriesService(
        countries_repository=CountriesRepository(db_pool),
        settings=settings,
    )

    countries = await service.list_countries()
    assert countries

    geojson = service.get_geojson()
    assert geojson['type'] == 'FeatureCollection'
    assert geojson['features']


def test_get_geojson_uses_project_root_for_relative_path(settings, monkeypatch, tmp_path) -> None:
    service = CountriesService(
        countries_repository=None,  # type: ignore[arg-type]
        settings=settings,
    )

    monkeypatch.chdir(tmp_path)

    geojson = service.get_geojson()
    assert geojson['type'] == 'FeatureCollection'
    assert geojson['features']
