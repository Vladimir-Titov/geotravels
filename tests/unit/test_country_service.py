from __future__ import annotations

import pytest

from app.repositories.countries import CountriesRepository
from app.services.countries import CountriesService


@pytest.mark.asyncio
async def test_list_countries_paginated(db_pool) -> None:
    service = CountriesService(countries_repository=CountriesRepository(db_pool))

    result = await service.list_countries(limit=5, offset=0)

    assert result.items
    assert len(result.items) <= 5
    assert result.pagination.limit == 5
    assert result.pagination.offset == 0
    assert result.pagination.total >= len(result.items)


@pytest.mark.asyncio
async def test_list_countries_filter_by_iso(db_pool) -> None:
    service = CountriesService(countries_repository=CountriesRepository(db_pool))

    result = await service.list_countries(limit=10, offset=0, iso_a2='FR')

    assert len(result.items) == 1
    assert result.items[0]['iso_a2'] == 'FR'
    assert result.pagination.total == 1
