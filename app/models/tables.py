from __future__ import annotations

from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, Index, MetaData, String, Table, Uuid, func

metadata = MetaData()

users_table = Table(
    'users',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('email', String(length=320), nullable=True),
    Column('password_hash', String(length=64), nullable=True),
    Column('created_at', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('telegram_id', BigInteger(), nullable=True),
    Index('idx_unique_email', 'email', unique=True, postgresql_where=Column('email').is_not(None)),
)

countries_table = Table(
    'countries',
    metadata,
    Column('iso_a2', String(length=2), primary_key=True),
    Column('name', String(length=128), nullable=False),
)

visits_table = Table(
    'visits',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('user_id', Uuid(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('country_code', ForeignKey('countries.iso_a2', ondelete='RESTRICT'), nullable=False),
    Column('marked_at', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('trip_date', Date, nullable=True),
    Index('idx_user_id', 'user_id'),
    Index('idx_country_code', 'country_code'),
)
