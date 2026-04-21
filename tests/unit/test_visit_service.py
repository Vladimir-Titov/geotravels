from __future__ import annotations

from datetime import date
from uuid import UUID, uuid4

import pytest

from app.repositories.files import FilesRepository
from app.repositories.users import UsersRepository
from app.repositories.visits import VisitsRepository
from app.repositories.visits_cities import VisitsCitiesRepository
from app.services.exceptions import NotFoundError
from app.services.visits import VisitsService


async def _create_user(db_pool) -> UUID:
    users_repo = UsersRepository(db_pool)
    return (await users_repo.create(email=f'{uuid4()}@example.com'))['id']


@pytest.mark.asyncio
async def test_visit_crud_for_current_user(db_pool) -> None:
    user_id = await _create_user(db_pool)
    service = VisitsService(
        visits_repository=VisitsRepository(db_pool),
        visits_cities_repository=VisitsCitiesRepository(db_pool),
        files_repository=FilesRepository(db_pool),
    )

    created = await service.create_visit(
        user_id=user_id,
        country_code='FR',
        city_id=None,
        trip_date=date(2025, 1, 2),
    )
    assert created['country_code'] == 'FR'

    listed = await service.list_visits(user_id=user_id, limit=100, offset=0)
    assert len(listed.items) == 1
    assert listed.pagination.total == 1

    loaded = await service.get_visit_by_id(visit_id=created['id'], user_id=user_id)
    assert loaded['id'] == created['id']

    updated = await service.update_visit_by_id(
        visit_id=created['id'],
        user_id=user_id,
        trip_date=date(2025, 1, 3),
    )
    assert updated['trip_date'] == date(2025, 1, 3)

    await service.delete_visit_by_id(visit_id=created['id'], user_id=user_id)

    after_delete = await service.list_visits(user_id=user_id, limit=100, offset=0)
    assert after_delete.items == []
    assert after_delete.pagination.total == 0


@pytest.mark.asyncio
async def test_visit_scope_isolated_by_user(db_pool) -> None:
    owner_id = await _create_user(db_pool)
    stranger_id = await _create_user(db_pool)
    service = VisitsService(
        visits_repository=VisitsRepository(db_pool),
        visits_cities_repository=VisitsCitiesRepository(db_pool),
        files_repository=FilesRepository(db_pool),
    )

    created = await service.create_visit(
        user_id=owner_id,
        country_code='FR',
        city_id=None,
        trip_date=None,
    )

    with pytest.raises(NotFoundError):
        await service.get_visit_by_id(visit_id=created['id'], user_id=stranger_id)

    with pytest.raises(NotFoundError):
        await service.update_visit_by_id(
            visit_id=created['id'],
            user_id=stranger_id,
            country_code='DE',
        )

    with pytest.raises(NotFoundError):
        await service.delete_visit_by_id(visit_id=created['id'], user_id=stranger_id)
