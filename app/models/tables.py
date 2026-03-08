from __future__ import annotations

from sqlalchemy import Column, Date, DateTime, ForeignKey, Index, MetaData, String, Table, Uuid, func

metadata = MetaData()

users_table = Table(
    'users',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('email', String(length=320), nullable=False, unique=True),
    Column('password_hash', String(length=64), nullable=False),
    Column('created_at', DateTime(timezone=True), nullable=False, server_default=func.now()),
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
)

Index('ix_visits_user_id', visits_table.c.user_id)
Index('ix_visits_country_code', visits_table.c.country_code)
