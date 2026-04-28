from uuid import UUID, uuid4

import pytest

from app.models.tables import CheckListStatus, FileVisibility
from app.repositories.files import FilesRepository
from app.repositories.users import UsersRepository
from app.repositories.visits import VisitsRepository
from app.repositories.visits_checklist import VisitsChecklistRepository
from app.repositories.visits_cities import VisitsCitiesRepository
from app.repositories.visits_places import VisitsPlacesRepository
from app.repositories.visits_places_files import VisitsPlacesFilesRepository
from app.services.exceptions import ConflictError, NotFoundError, ServiceError
from app.services.visits import VisitsService
from app.services.visits_checklist import VisitsChecklistService
from app.services.visits_places import VisitsPlacesService
from app.services.visits_places_files import VisitsPlacesFilesService


async def _create_user(db_pool) -> UUID:
    users_repo = UsersRepository(db_pool)
    return (await users_repo.create(email=f'{uuid4()}@example.com'))['id']


async def _create_visit(db_pool, user_id: UUID, country_code: str = 'FR') -> dict:
    service = VisitsService(
        visits_repository=VisitsRepository(db_pool),
        visits_cities_repository=VisitsCitiesRepository(db_pool),
        files_repository=FilesRepository(db_pool),
    )
    return await service.create_visit(user_id=user_id, country_code=country_code)


@pytest.mark.asyncio
async def test_visits_checklist_service_defaults_and_scopes_by_user(db_pool) -> None:
    owner_id = await _create_user(db_pool)
    stranger_id = await _create_user(db_pool)
    visit = await _create_visit(db_pool, owner_id)
    service = VisitsChecklistService(
        visits_checklist_repository=VisitsChecklistRepository(db_pool),
        visits_repository=VisitsRepository(db_pool),
    )

    created = await service.create_item(
        user_id=owner_id,
        visit_id=visit['id'],
        content='  Pack documents  ',
    )
    assert created['content'] == 'Pack documents'
    assert created['status'] == CheckListStatus.TO_DO

    updated = await service.update_item_by_id(
        checklist_id=created['id'],
        user_id=owner_id,
        status=CheckListStatus.DONE,
    )
    assert updated['status'] == CheckListStatus.DONE

    with pytest.raises(NotFoundError):
        await service.get_item_by_id(checklist_id=created['id'], user_id=stranger_id)


@pytest.mark.asyncio
async def test_visits_places_service_duplicate_title_raises_conflict(db_pool) -> None:
    owner_id = await _create_user(db_pool)
    visit = await _create_visit(db_pool, owner_id)
    service = VisitsPlacesService(
        visits_places_repository=VisitsPlacesRepository(db_pool),
        visits_repository=VisitsRepository(db_pool),
    )

    created = await service.create_place(
        user_id=owner_id,
        visit_id=visit['id'],
        title='  Eiffel Tower  ',
    )
    assert created['title'] == 'Eiffel Tower'
    assert created['is_visited'] is False

    with pytest.raises(ConflictError):
        await service.create_place(
            user_id=owner_id,
            visit_id=visit['id'],
            title='Eiffel Tower',
        )


@pytest.mark.asyncio
async def test_visits_places_files_service_validates_visit_and_duplicate_relation(db_pool) -> None:
    owner_id = await _create_user(db_pool)
    visit = await _create_visit(db_pool, owner_id, country_code='FR')
    other_visit = await _create_visit(db_pool, owner_id, country_code='IT')

    places_service = VisitsPlacesService(
        visits_places_repository=VisitsPlacesRepository(db_pool),
        visits_repository=VisitsRepository(db_pool),
    )
    place = await places_service.create_place(
        user_id=owner_id,
        visit_id=visit['id'],
        title='Louvre',
    )

    files_repository = FilesRepository(db_pool)
    same_visit_file = await files_repository.create_file(
        file_url='memory://same-visit',
        filename='same.jpg',
        file_type='image/jpeg',
    )
    await files_repository.create_file_visit_relation(
        file_id=same_visit_file['id'],
        visit_id=visit['id'],
        user_id=owner_id,
        is_private=False,
        visibility=FileVisibility.PUBLIC,
    )

    foreign_visit_file = await files_repository.create_file(
        file_url='memory://other-visit',
        filename='other.jpg',
        file_type='image/jpeg',
    )
    await files_repository.create_file_visit_relation(
        file_id=foreign_visit_file['id'],
        visit_id=other_visit['id'],
        user_id=owner_id,
        is_private=False,
        visibility=FileVisibility.PUBLIC,
    )

    service = VisitsPlacesFilesService(
        visits_places_files_repository=VisitsPlacesFilesRepository(db_pool),
        visits_places_repository=VisitsPlacesRepository(db_pool),
        files_repository=files_repository,
    )

    created = await service.create_relation(
        user_id=owner_id,
        visit_place_id=place['id'],
        file_id=same_visit_file['id'],
    )
    assert created['visit_place_id'] == place['id']

    with pytest.raises(ConflictError):
        await service.create_relation(
            user_id=owner_id,
            visit_place_id=place['id'],
            file_id=same_visit_file['id'],
        )

    with pytest.raises(ServiceError):
        await service.create_relation(
            user_id=owner_id,
            visit_place_id=place['id'],
            file_id=foreign_visit_file['id'],
        )
