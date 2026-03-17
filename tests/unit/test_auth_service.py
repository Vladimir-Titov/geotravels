from __future__ import annotations

from uuid import uuid4

import pytest

from app.models.tables import users_table
from app.repositories.telegram_users import TelegramUsersRepository
from app.repositories.users import UsersRepository
from app.services.auth import AuthService
from app.services.exceptions import AuthenticationError, ConflictError


@pytest.mark.asyncio
async def test_register_and_login(db_pool, settings) -> None:
    service = AuthService(users_repository=UsersRepository(db_pool), telegram_users_repository=TelegramUsersRepository(db_pool), settings=settings)

    register_result = await service.register(email='user@example.com', password='secret123')
    assert register_result['access_token']
    assert register_result['refresh_token']

    login_result = await service.login(email='user@example.com', password='secret123')
    assert login_result['access_token']
    assert login_result['refresh_token']


@pytest.mark.asyncio
async def test_register_duplicate_email(db_pool, settings) -> None:
    service = AuthService(users_repository=UsersRepository(db_pool), telegram_users_repository=TelegramUsersRepository(db_pool), settings=settings)

    await service.register(email='dupe@example.com', password='secret123')

    with pytest.raises(ConflictError):
        await service.register(email='dupe@example.com', password='secret123')


@pytest.mark.asyncio
async def test_refresh_returns_access_token(db_pool, settings) -> None:
    service = AuthService(users_repository=UsersRepository(db_pool), telegram_users_repository=TelegramUsersRepository(db_pool), settings=settings)

    tokens = await service.register(email='refresh@example.com', password='secret123')
    refreshed = await service.refresh(tokens['refresh_token'])

    assert refreshed['access_token']
    assert refreshed['token_type'] == 'bearer'


@pytest.mark.asyncio
async def test_refresh_deleted_user_raises_authentication_error(db_pool, settings) -> None:
    service = AuthService(users_repository=UsersRepository(db_pool), telegram_users_repository=TelegramUsersRepository(db_pool), settings=settings)

    tokens = await service.register(email='deleted@example.com', password='secret123')
    user_id = service.get_user_id_from_access_token(tokens['access_token'])

    async with db_pool.connection() as conn:
        await conn.execute(users_table.delete().where(users_table.c.id == user_id))

    with pytest.raises(AuthenticationError):
        await service.refresh(tokens['refresh_token'])


@pytest.mark.asyncio
async def test_register_translates_insert_conflict_to_conflict_error(db_pool, settings, monkeypatch) -> None:
    users_repository = UsersRepository(db_pool)
    service = AuthService(users_repository=users_repository, telegram_users_repository=TelegramUsersRepository(db_pool), settings=settings)
    existing_user = {'id': uuid4()}
    call_count = 0

    async def fake_get_by_email(_: str):
        nonlocal call_count
        call_count += 1
        return None if call_count == 1 else existing_user

    async def fake_create(email: str, password_hash: str):
        del email, password_hash
        raise RuntimeError('duplicate key')

    monkeypatch.setattr(users_repository, 'get_by_email', fake_get_by_email)
    monkeypatch.setattr(users_repository, 'create', fake_create)

    with pytest.raises(ConflictError):
        await service.register(email='racy@example.com', password='secret123')


@pytest.mark.asyncio
async def test_login_with_wrong_password(db_pool, settings) -> None:
    service = AuthService(users_repository=UsersRepository(db_pool), telegram_users_repository=TelegramUsersRepository(db_pool), settings=settings)

    await service.register(email='badpass@example.com', password='secret123')

    with pytest.raises(AuthenticationError):
        await service.login(email='badpass@example.com', password='wrongpass')
