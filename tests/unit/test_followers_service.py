from __future__ import annotations

from uuid import UUID, uuid4

import pytest
import pytest_asyncio

from app.repositories.followers import FollowersRepository
from app.repositories.users import UsersRepository
from app.services.exceptions import ConflictError, NotFoundError, ServiceError
from app.services.followers import FollowersService


async def _create_user(db_pool) -> UUID:
    users_repo = UsersRepository(db_pool)
    return (await users_repo.create(email=f'{uuid4()}@example.com'))['id']


@pytest_asyncio.fixture
async def followers_service(db_pool) -> FollowersService:
    return FollowersService(
        followers_repository=FollowersRepository(db_pool),
        users_repository=UsersRepository(db_pool),
    )


@pytest.mark.asyncio
async def test_subscribe_creates_relation(followers_service, db_pool) -> None:
    follower_id = await _create_user(db_pool)
    following_id = await _create_user(db_pool)

    relation = await followers_service.subscribe(
        follower_id=follower_id,
        following_id=following_id,
    )

    assert relation['follower_id'] == follower_id
    assert relation['following_id'] == following_id


@pytest.mark.asyncio
async def test_unsubscribe_returns_removed_relation(followers_service, db_pool) -> None:
    follower_id = await _create_user(db_pool)
    following_id = await _create_user(db_pool)
    created = await followers_service.subscribe(
        follower_id=follower_id,
        following_id=following_id,
    )

    removed = await followers_service.unsubscribe(
        follower_id=follower_id,
        following_id=following_id,
    )

    assert removed['id'] == created['id']
    assert removed['follower_id'] == follower_id
    assert removed['following_id'] == following_id


@pytest.mark.asyncio
async def test_unsubscribe_removes_relation_from_listing(followers_service, db_pool) -> None:
    follower_id = await _create_user(db_pool)
    following_id = await _create_user(db_pool)
    await followers_service.subscribe(
        follower_id=follower_id,
        following_id=following_id,
    )

    await followers_service.unsubscribe(
        follower_id=follower_id,
        following_id=following_id,
    )

    own_list = await followers_service.list_followers(limit=100, offset=0, follower_id=follower_id)
    assert own_list.items == []
    assert own_list.pagination.total == 0


@pytest.mark.asyncio
async def test_subscribe_self_raises_validation_error(followers_service, db_pool) -> None:
    follower_id = await _create_user(db_pool)

    with pytest.raises(ServiceError):
        await followers_service.subscribe(follower_id=follower_id, following_id=follower_id)


@pytest.mark.asyncio
async def test_subscribe_missing_user_raises_not_found(followers_service, db_pool) -> None:
    follower_id = await _create_user(db_pool)

    with pytest.raises(NotFoundError):
        await followers_service.subscribe(
            follower_id=follower_id,
            following_id=UUID('00000000-0000-0000-0000-000000000000'),
        )


@pytest.mark.asyncio
async def test_subscribe_duplicate_raises_conflict(followers_service, db_pool) -> None:
    follower_id = await _create_user(db_pool)
    following_id = await _create_user(db_pool)

    await followers_service.subscribe(follower_id=follower_id, following_id=following_id)

    with pytest.raises(ConflictError):
        await followers_service.subscribe(follower_id=follower_id, following_id=following_id)


@pytest.mark.asyncio
async def test_unsubscribe_missing_relation_raises_not_found(followers_service, db_pool) -> None:
    follower_id = await _create_user(db_pool)
    following_id = await _create_user(db_pool)

    with pytest.raises(NotFoundError):
        await followers_service.unsubscribe(
            follower_id=follower_id,
            following_id=following_id,
        )


@pytest.mark.asyncio
async def test_listing_supports_own_and_foreign_filters(followers_service, db_pool) -> None:
    me_id = await _create_user(db_pool)
    other_id = await _create_user(db_pool)
    shared_target = await _create_user(db_pool)
    extra_target = await _create_user(db_pool)

    await followers_service.subscribe(follower_id=me_id, following_id=shared_target)
    await followers_service.subscribe(follower_id=other_id, following_id=shared_target)
    await followers_service.subscribe(follower_id=other_id, following_id=extra_target)

    own = await followers_service.list_followers(limit=100, offset=0, follower_id=me_id)
    assert own.pagination.total == 1
    assert {item['following_id'] for item in own.items} == {shared_target}

    foreign = await followers_service.list_followers(limit=100, offset=0, follower_id=other_id)
    assert foreign.pagination.total == 2
    assert {item['following_id'] for item in foreign.items} == {shared_target, extra_target}
