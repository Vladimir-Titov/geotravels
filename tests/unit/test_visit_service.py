from __future__ import annotations

from datetime import date
from uuid import UUID

import pytest

from app.repositories.countries import CountriesRepository
from app.repositories.users import UsersRepository
from app.repositories.visits import VisitsRepository
from app.services.exceptions import NotFoundError
from app.services.visits import VisitsService
from helpers.security import hash_password


async def _create_user(db_pool) -> UUID:
    users_repo = UsersRepository(db_pool)
    return (await users_repo.create(email='visits@example.com', password_hash=hash_password('secret123')))['id']


@pytest.mark.asyncio
async def test_mark_visit_and_list(db_pool) -> None:
    user_id = await _create_user(db_pool)
    service = VisitsService(
        visits_repository=VisitsRepository(db_pool),
        countries_repository=CountriesRepository(db_pool),
    )

    visit = await service.mark_visited(
        user_id=user_id,
        country_code='fr',
        trip_date=date(2025, 1, 2),
    )
    assert visit['country_code'] == 'FR'

    data = await service.list_visits(user_id=user_id)
    assert len(data['visits']) == 1
    assert data['visited_country_codes'] == ['FR']


@pytest.mark.asyncio
async def test_mark_unknown_country_raises_not_found(db_pool) -> None:
    user_id = await _create_user(db_pool)
    service = VisitsService(
        visits_repository=VisitsRepository(db_pool),
        countries_repository=CountriesRepository(db_pool),
    )

    with pytest.raises(NotFoundError):
        await service.mark_visited(user_id=user_id, country_code='zz', trip_date=None)
