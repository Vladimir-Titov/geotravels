from datetime import date
from uuid import UUID, uuid4

import pytest

from app.models.tables import VisitStatus
from app.repositories.cities import CitiesRepository
from app.repositories.files import FilesRepository
from app.repositories.users import UsersRepository
from app.repositories.visits import VisitsRepository
from app.repositories.visits_cities import VisitsCitiesRepository
from app.services.exceptions import NotFoundError, ServiceError
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
        trip_start=date(2025, 1, 2),
    )
    assert created['country_code'] == 'FR'
    assert created['status'] == VisitStatus.VISITED

    listed = await service.list_visits(user_id=user_id, limit=100, offset=0)
    assert len(listed.items) == 1
    assert listed.pagination.total == 1

    loaded = await service.get_visit_by_id(visit_id=created['id'], user_id=user_id)
    assert loaded['id'] == created['id']

    updated = await service.update_visit_by_id(
        visit_id=created['id'],
        user_id=user_id,
        trip_start=date(2025, 1, 3),
        status=VisitStatus.PLANNED,
    )
    assert updated['trip_start'] == date(2025, 1, 3)
    assert updated['status'] == VisitStatus.PLANNED

    await service.delete_visit_by_id(visit_id=created['id'], user_id=user_id)

    after_delete = await service.list_visits(user_id=user_id, limit=100, offset=0)
    assert after_delete.items == []
    assert after_delete.pagination.total == 0


@pytest.mark.asyncio
async def test_visit_dates_can_be_empty(db_pool) -> None:
    user_id = await _create_user(db_pool)
    service = VisitsService(
        visits_repository=VisitsRepository(db_pool),
        visits_cities_repository=VisitsCitiesRepository(db_pool),
        files_repository=FilesRepository(db_pool),
    )

    created = await service.create_visit(
        user_id=user_id,
        country_code='FR',
        trip_start=None,
        trip_end=None,
    )
    assert created['trip_start'] is None
    assert created['trip_end'] is None

    updated = await service.update_visit_by_id(
        visit_id=created['id'],
        user_id=user_id,
        trip_start=None,
        trip_end=None,
    )
    assert updated['trip_start'] is None
    assert updated['trip_end'] is None


@pytest.mark.asyncio
async def test_visit_rejects_invalid_trip_range(db_pool) -> None:
    user_id = await _create_user(db_pool)
    service = VisitsService(
        visits_repository=VisitsRepository(db_pool),
        visits_cities_repository=VisitsCitiesRepository(db_pool),
        files_repository=FilesRepository(db_pool),
    )

    with pytest.raises(ServiceError, match='trip_end cannot be earlier than trip_start'):
        await service.create_visit(
            user_id=user_id,
            country_code='FR',
            trip_start=date(2025, 1, 3),
            trip_end=date(2025, 1, 2),
        )


@pytest.mark.asyncio
async def test_visit_city_ids_are_stored_in_link_table(db_pool) -> None:
    user_id = await _create_user(db_pool)
    paris_id = uuid4()
    lyon_id = uuid4()
    cities_repository = CitiesRepository(db_pool)
    visits_cities_repository = VisitsCitiesRepository(db_pool)
    service = VisitsService(
        visits_repository=VisitsRepository(db_pool),
        visits_cities_repository=visits_cities_repository,
        files_repository=FilesRepository(db_pool),
    )

    await cities_repository.create(id=paris_id, country_code='FR', name='Paris')
    await cities_repository.create(id=lyon_id, country_code='FR', name='Lyon')

    created = await service.create_visit(
        user_id=user_id,
        country_code='FR',
        city_ids=[paris_id, lyon_id, paris_id],
    )

    assert created['city_ids'] == [paris_id, lyon_id]
    assert await visits_cities_repository.list_city_ids_for_visits([created['id']]) == {
        created['id']: [paris_id, lyon_id]
    }

    filtered = await service.list_visits(user_id=user_id, limit=100, offset=0, city_ids_in=[lyon_id])
    assert [item['id'] for item in filtered.items] == [created['id']]


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
        trip_start=None,
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
