from sqlalchemy import BigInteger, Column, DateTime, String, Table, func

from app.models.base import metadata

telegram_users = Table(
    'telegram_users',
    metadata,
    Column('telegram_id', BigInteger(), primary_key=True, unique=True),
    Column('username', String(length=32), nullable=True),
    Column('first_name', String(length=64), nullable=True),
    Column('last_name', String(length=64), nullable=True),
    Column('language_code', String(length=10), nullable=True),
    Column('photo_url', String(length=128), nullable=True),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
)
