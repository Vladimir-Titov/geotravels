from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    Uuid,
    func,
)

metadata = MetaData(schema='tripmark')

users = Table(
    'users',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('email', String(length=320), nullable=True),
    Column(
        'telegram_user_id', BigInteger(), ForeignKey('telegram_users.telegram_id', ondelete='SET NULL'), nullable=True
    ),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
    Index('idx_unique_email', 'email', unique=True, postgresql_where=Column('email').is_not(None)),
)

countries = Table(
    'countries',
    metadata,
    Column('iso_a2', String(length=2), primary_key=True),
    Column('name', String(length=128), nullable=False),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
)

visits = Table(
    'visits',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('user_id', Uuid(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('country_code', ForeignKey('countries.iso_a2', ondelete='RESTRICT'), nullable=False),
    Column('marked_at', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('trip_date', Date, nullable=True),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
    Index('idx_user_id', 'user_id'),
    Index('idx_country_code', 'country_code'),
)

otp_requests = Table(
    'otp_requests',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('contact', String(length=320), nullable=False),
    Column('code_hash', String(length=64), nullable=False),
    Column('expires_at', DateTime(timezone=True), nullable=False),
    Column('attempts', Integer(), nullable=False, server_default='0'),
    Column('status', String(length=20), nullable=False, server_default='sent'),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
)

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
