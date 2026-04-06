from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from app.repositories.followers import FollowersRepository
from app.repositories.users import UsersRepository
from app.services.exceptions import ConflictError, NotFoundError, ServiceError
from app.services.followers import FollowersService


async def _create_user(db_pool) -> UUID:
    users_repo = UsersRepository(db_pool)
    return (await users_repo.create(email=f'{uuid4()}@example.com'))['id']


@pytest.mark.asyncio
async def test_followers_subscribe_unsubscribe_flow(db_pool) -> None:
    follower_id = await _create_user(db_pool)
    following_id = await _create_user(db_pool)

    service = FollowersService(
        followers_repository=FollowersRepository(db_pool),
        users_repository=UsersRepository(db_pool),
    )

    relation = await service.subscribe(
        follower_id=follower_id,
        following_id=following_id,
    )
    assert relation['follower_id'] == follower_id
    assert relation['following_id'] == following_id

    own_list = await service.list_followers(limit=100, offset=0, follower_id=follower_id)
    assert own_list.pagination.total == 1
    assert len(own_list.items) == 1
    assert own_list.items[0]['following_id'] == following_id

    await service.unsubscribe(
        follower_id=follower_id,
        following_id=following_id,
    )

    empty = await service.list_followers(limit=100, offset=0, follower_id=follower_id)
    assert empty.items == []
    assert empty.pagination.total == 0


@pytest.mark.asyncio
async def test_followers_subscribe_guards(db_pool) -> None:
    follower_id = await _create_user(db_pool)
    following_id = await _create_user(db_pool)

    service = FollowersService(
        followers_repository=FollowersRepository(db_pool),
        users_repository=UsersRepository(db_pool),
    )

    with pytest.raises(ServiceError):
        await service.subscribe(follower_id=follower_id, following_id=follower_id)

    with pytest.raises(NotFoundError):
        await service.subscribe(
            follower_id=follower_id,
            following_id=UUID('00000000-0000-0000-0000-000000000000'),
        )

    await service.subscribe(follower_id=follower_id, following_id=following_id)

    with pytest.raises(ConflictError):
        await service.subscribe(follower_id=follower_id, following_id=following_id)

    with pytest.raises(NotFoundError):
        await service.unsubscribe(
            follower_id=following_id,
            following_id=follower_id,
        )


@pytest.mark.asyncio
async def test_followers_listing_supports_own_and_foreign_filters(db_pool) -> None:
    me_id = await _create_user(db_pool)
    other_id = await _create_user(db_pool)
    shared_target = await _create_user(db_pool)
    extra_target = await _create_user(db_pool)

    service = FollowersService(
        followers_repository=FollowersRepository(db_pool),
        users_repository=UsersRepository(db_pool),
    )

    await service.subscribe(follower_id=me_id, following_id=shared_target)
    await service.subscribe(follower_id=other_id, following_id=shared_target)
    await service.subscribe(follower_id=other_id, following_id=extra_target)

    own = await service.list_followers(limit=100, offset=0, follower_id=me_id)
    assert own.pagination.total == 1
    assert {item['following_id'] for item in own.items} == {shared_target}

    foreign = await service.list_followers(limit=100, offset=0, follower_id=other_id)
    assert foreign.pagination.total == 2
    assert {item['following_id'] for item in foreign.items} == {shared_target, extra_target}
