from __future__ import annotations

from datetime import date
from uuid import UUID, uuid4

import pytest

from app.repositories.achievements import AchievementsRepository
from app.repositories.files import FilesRepository
from app.repositories.followers import FollowersRepository
from app.repositories.users import UsersRepository
from app.repositories.users_achievements import UsersAchievementsRepository
from app.repositories.visits import VisitsRepository
from app.services.achievements import AchievementsService


async def _create_user(db_pool) -> UUID:
    users_repo = UsersRepository(db_pool)
    return (await users_repo.create(email=f'{uuid4()}@example.com'))['id']


@pytest.mark.asyncio
async def test_list_achievements_and_my_earned(db_pool) -> None:
    service = AchievementsService(
        achievements_repository=AchievementsRepository(db_pool),
        users_achievements_repository=UsersAchievementsRepository(db_pool),
        visits_repository=VisitsRepository(db_pool),
        files_repository=FilesRepository(db_pool),
        followers_repository=FollowersRepository(db_pool),
        users_repository=UsersRepository(db_pool),
    )
    achievements_repository = AchievementsRepository(db_pool)
    users_achievements_repository = UsersAchievementsRepository(db_pool)

    me_id = await _create_user(db_pool)
    other_id = await _create_user(db_pool)

    earned = await achievements_repository.create(
        title='First Trip',
        description='Complete your first trip',
        logo_url='https://cdn.example.com/first-trip.png',
    )
    not_earned = await achievements_repository.create(
        title='Explorer',
        description='Visit 10 countries',
    )

    await users_achievements_repository.create(user_id=me_id, achievements_id=earned['id'])
    await users_achievements_repository.create(user_id=other_id, achievements_id=not_earned['id'])

    all_achievements = await service.list_achievements(limit=100, offset=0)
    all_ids = {item['id'] for item in all_achievements.items}
    assert {earned['id'], not_earned['id']}.issubset(all_ids)

    sorted_by_title = await service.list_achievements(limit=100, offset=0, order_by='title')
    titles = [item['title'] for item in sorted_by_title.items]
    assert 'Explorer' in titles
    assert 'First Trip' in titles

    filtered_all = await service.list_achievements(limit=100, offset=0, title='Explorer')
    assert filtered_all.pagination.total == 1
    assert filtered_all.items[0]['id'] == not_earned['id']

    my_achievements = await service.list_user_achievements(user_id=me_id, limit=100, offset=0)
    assert my_achievements.pagination.total == 1
    assert my_achievements.items[0]['id'] == earned['id']
    assert my_achievements.items[0]['user_id'] == me_id
    assert my_achievements.items[0]['complete_at'] is not None

    filtered_my = await service.list_user_achievements(user_id=me_id, limit=100, offset=0, title='First Trip')
    assert filtered_my.pagination.total == 1
    assert filtered_my.items[0]['id'] == earned['id']


@pytest.mark.asyncio
async def test_auto_award_first_visit_and_progress(db_pool) -> None:
    service = AchievementsService(
        achievements_repository=AchievementsRepository(db_pool),
        users_achievements_repository=UsersAchievementsRepository(db_pool),
        visits_repository=VisitsRepository(db_pool),
        files_repository=FilesRepository(db_pool),
        followers_repository=FollowersRepository(db_pool),
        users_repository=UsersRepository(db_pool),
    )
    visits_repository = VisitsRepository(db_pool)

    user_id = await _create_user(db_pool)
    await visits_repository.create(
        user_id=user_id,
        country_code='FR',
        title='Paris',
        description=None,
        visibility='private',
        date_from=date(2026, 1, 1),
        date_to=None,
        city_id=None,
        trip_date=date(2026, 1, 1),
    )

    awarded = await service.auto_award_for_user(user_id=user_id)
    assert len(awarded) == 1

    progress = await service.get_next_progress(user_id=user_id)
    assert progress is not None
    assert progress['current_value'] >= 1
    assert progress['target_value'] >= progress['current_value']
