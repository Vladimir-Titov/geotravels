from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, String, Table, Uuid, func

from app.models.base import metadata

users = Table(
    'users',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('email', String(length=320), nullable=True),
    Column('first_name', String(length=64), nullable=True),
    Column('last_name', String(length=64), nullable=True),
    Column('username', String(length=32), nullable=True),
    Column(
        'telegram_user_id', BigInteger(), ForeignKey('telegram_users.telegram_id', ondelete='SET NULL'), nullable=True
    ),
    Column(
        'yandex_user_id', String(length=64), ForeignKey('yandex_users.yandex_id', ondelete='SET NULL'), nullable=True
    ),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
    Index('idx_unique_email', 'email', unique=True, postgresql_where=Column('email').is_not(None)),
)
