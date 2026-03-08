from __future__ import annotations

import pytest

from app.repositories.users import UsersRepository
from app.services.auth import AuthService
from app.services.exceptions import AuthenticationError, ConflictError


@pytest.mark.asyncio
async def test_register_and_login(db_pool, settings) -> None:
    service = AuthService(users_repository=UsersRepository(db_pool), settings=settings)

    register_result = await service.register(email='user@example.com', password='secret123')
    assert register_result['access_token']
    assert register_result['refresh_token']

    login_result = await service.login(email='user@example.com', password='secret123')
    assert login_result['access_token']
    assert login_result['refresh_token']


@pytest.mark.asyncio
async def test_register_duplicate_email(db_pool, settings) -> None:
    service = AuthService(users_repository=UsersRepository(db_pool), settings=settings)

    await service.register(email='dupe@example.com', password='secret123')

    with pytest.raises(ConflictError):
        await service.register(email='dupe@example.com', password='secret123')


@pytest.mark.asyncio
async def test_refresh_returns_access_token(db_pool, settings) -> None:
    service = AuthService(users_repository=UsersRepository(db_pool), settings=settings)

    tokens = await service.register(email='refresh@example.com', password='secret123')
    refreshed = await service.refresh(tokens['refresh_token'])

    assert refreshed['access_token']
    assert refreshed['token_type'] == 'bearer'


@pytest.mark.asyncio
async def test_login_with_wrong_password(db_pool, settings) -> None:
    service = AuthService(users_repository=UsersRepository(db_pool), settings=settings)

    await service.register(email='badpass@example.com', password='secret123')

    with pytest.raises(AuthenticationError):
        await service.login(email='badpass@example.com', password='wrongpass')
