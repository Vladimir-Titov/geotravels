import hashlib
from uuid import uuid4

import arrow
import pytest

from app.models import OtpRequestStatus, users
from app.repositories.otp_requests import OtpRequestsRepository
from app.repositories.telegram_users import TelegramUsersRepository
from app.repositories.users import UsersRepository
from app.services.auth import AuthService
from app.services.exceptions import AppError, AuthenticationError, CountdownError
from app.services.otp_sender import MockOtpSender


class FailingOtpSender:
    async def send(self, contact: str, code: str) -> None:  # noqa: ARG002
        raise RuntimeError('send failed')


def make_service(db_pool, settings, otp_sender=None) -> AuthService:
    return AuthService(
        users_repository=UsersRepository(db_pool),
        telegram_users_repository=TelegramUsersRepository(db_pool),
        otp_requests_repository=OtpRequestsRepository(db_pool),
        otp_sender=otp_sender or MockOtpSender(),
        settings=settings,
    )


@pytest.mark.asyncio
async def test_request_otp_creates_record_and_returns_otp_id(db_pool, settings) -> None:
    service = make_service(db_pool, settings)
    result = await service.request_otp('user@example.com')

    assert 'otp_id' in result
    assert result['message'] == 'OTP sent'


@pytest.mark.asyncio
async def test_request_otp_rate_limit_raises_error(db_pool, settings) -> None:
    service = make_service(db_pool, settings)
    await service.request_otp('ratelimit@example.com')

    with pytest.raises(CountdownError, match='Please wait'):
        await service.request_otp('ratelimit@example.com')


@pytest.mark.asyncio
async def test_request_otp_sender_failure_raises_and_marks_request_failed(db_pool, settings) -> None:
    repo = OtpRequestsRepository(db_pool)
    service = make_service(db_pool, settings, otp_sender=FailingOtpSender())

    with pytest.raises(AppError, match='Failed to send OTP'):
        await service.request_otp('senderfail@example.com')

    rows = await repo.search(contact='senderfail@example.com')
    assert len(rows) == 1
    assert rows[0]['status'] == OtpRequestStatus.FAILED


@pytest.mark.asyncio
async def test_verify_otp_returns_tokens(db_pool, settings) -> None:
    service = make_service(db_pool, settings)
    otp_result = await service.request_otp('verify@example.com')

    tokens = await service.verify_otp(
        otp_id=otp_result['otp_id'],
        code=settings.otp.otp_mock_code,
    )

    assert tokens['access_token']
    assert tokens['refresh_token']
    assert tokens['token_type'] == 'bearer'


@pytest.mark.asyncio
async def test_verify_otp_wrong_code_raises_authentication_error(db_pool, settings) -> None:
    service = make_service(db_pool, settings)
    otp_result = await service.request_otp('wrongcode@example.com')

    with pytest.raises(AuthenticationError, match='Invalid code'):
        await service.verify_otp(otp_id=otp_result['otp_id'], code='000000')


@pytest.mark.asyncio
async def test_verify_otp_increments_attempts_on_wrong_code(db_pool, settings) -> None:
    repo = OtpRequestsRepository(db_pool)
    service = make_service(db_pool, settings)
    otp_result = await service.request_otp('attempts@example.com')
    otp_id = otp_result['otp_id']

    with pytest.raises(AuthenticationError):
        await service.verify_otp(otp_id=otp_id, code='000000')

    from uuid import UUID

    record = await repo.get_by_id(UUID(otp_id))
    assert record['attempts'] == 1


@pytest.mark.asyncio
async def test_verify_otp_max_attempts_exceeded_raises_error(db_pool, settings) -> None:
    from uuid import UUID

    repo = OtpRequestsRepository(db_pool)
    service = make_service(db_pool, settings)
    otp_result = await service.request_otp('maxattempts@example.com')
    otp_id = UUID(otp_result['otp_id'])

    for _ in range(settings.otp.otp_max_attempts):
        await repo.increment_attempts(otp_id)

    with pytest.raises(AuthenticationError, match='Too many'):
        await service.verify_otp(otp_id=otp_id, code=settings.otp.otp_mock_code)


@pytest.mark.asyncio
async def test_verify_otp_expired_raises_authentication_error(db_pool, settings) -> None:
    repo = OtpRequestsRepository(db_pool)
    expired_at = arrow.utcnow().shift(minutes=-1).datetime
    record = await repo.create(
        contact='expired@example.com',
        code_hash=hashlib.sha256('123456'.encode()).hexdigest(),
        expires_at=expired_at,
        status=OtpRequestStatus.SENT,
    )
    service = make_service(db_pool, settings)

    with pytest.raises(AuthenticationError, match='expired'):
        await service.verify_otp(otp_id=record['id'], code='123456')


@pytest.mark.asyncio
async def test_verify_otp_unknown_otp_id_raises_error(db_pool, settings) -> None:
    service = make_service(db_pool, settings)

    with pytest.raises(AuthenticationError):
        await service.verify_otp(otp_id=uuid4(), code='123456')


@pytest.mark.asyncio
async def test_verify_otp_creates_user_if_not_exists(db_pool, settings) -> None:
    service = make_service(db_pool, settings)
    otp_result = await service.request_otp('newuser@example.com')

    tokens = await service.verify_otp(
        otp_id=otp_result['otp_id'],
        code=settings.otp.otp_mock_code,
    )

    user_id = service.get_user_id_from_access_token(tokens['access_token'])
    user = await UsersRepository(db_pool).get_by_id(user_id)
    assert user['email'] == 'newuser@example.com'


@pytest.mark.asyncio
async def test_verify_otp_marks_record_done_after_success(db_pool, settings) -> None:
    from uuid import UUID

    repo = OtpRequestsRepository(db_pool)
    service = make_service(db_pool, settings)
    otp_result = await service.request_otp('deleterecord@example.com')
    otp_id = UUID(otp_result['otp_id'])

    await service.verify_otp(otp_id=otp_id, code=settings.otp.otp_mock_code)

    record = await repo.get_by_id(otp_id)
    assert record['status'] == OtpRequestStatus.DONE


@pytest.mark.asyncio
async def test_verify_otp_replay_is_rejected_after_success(db_pool, settings) -> None:
    from uuid import UUID

    service = make_service(db_pool, settings)
    otp_result = await service.request_otp('replay@example.com')
    otp_id = UUID(otp_result['otp_id'])

    await service.verify_otp(otp_id=otp_id, code=settings.otp.otp_mock_code)

    with pytest.raises(AuthenticationError, match='Invalid or expired OTP'):
        await service.verify_otp(otp_id=otp_id, code=settings.otp.otp_mock_code)


@pytest.mark.asyncio
async def test_refresh_returns_access_token(db_pool, settings) -> None:
    service = make_service(db_pool, settings)
    otp_result = await service.request_otp('refresh@example.com')
    tokens = await service.verify_otp(
        otp_id=otp_result['otp_id'],
        code=settings.otp.otp_mock_code,
    )

    refreshed = await service.refresh(tokens['refresh_token'])

    assert refreshed['access_token']
    assert refreshed['token_type'] == 'bearer'


@pytest.mark.asyncio
async def test_refresh_deleted_user_raises_authentication_error(db_pool, settings) -> None:
    service = make_service(db_pool, settings)
    otp_result = await service.request_otp('deleteduser@example.com')
    tokens = await service.verify_otp(
        otp_id=otp_result['otp_id'],
        code=settings.otp.otp_mock_code,
    )
    user_id = service.get_user_id_from_access_token(tokens['access_token'])

    async with db_pool.connection() as conn:
        await conn.execute(users.delete().where(users.c.id == user_id))

    with pytest.raises(AuthenticationError):
        await service.refresh(tokens['refresh_token'])
