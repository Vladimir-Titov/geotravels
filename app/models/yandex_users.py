from sqlalchemy import Column, DateTime, String, Table, func

from app.models.base import metadata

yandex_users = Table(
    'yandex_users',
    metadata,
    Column('yandex_id', String(length=64), primary_key=True, unique=True),
    Column('login', String(length=255), nullable=True),
    Column('default_email', String(length=320), nullable=True),
    Column('first_name', String(length=64), nullable=True),
    Column('last_name', String(length=64), nullable=True),
    Column('display_name', String(length=255), nullable=True),
    Column('real_name', String(length=255), nullable=True),
    Column('default_avatar_id', String(length=128), nullable=True),
    Column('client_id', String(length=128), nullable=True),
    Column('psuid', String(length=255), nullable=True),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
)
