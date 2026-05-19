from enum import StrEnum

from sqlalchemy import Column, Date, DateTime, ForeignKey, Index, String, Table, Text, Uuid, func

from app.models.base import metadata


class VisitStatus(StrEnum):
    PLANNED = 'planned'
    IN_TRIP = 'in_trip'
    VISITED = 'visited'


class VisitVisibility(StrEnum):
    PRIVATE = 'private'
    FOLLOWERS = 'followers'
    PUBLIC = 'public'


visits = Table(
    'visits',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('user_id', Uuid(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('country_code', String(length=2), ForeignKey('countries.iso_a2', ondelete='RESTRICT'), nullable=False),
    Column('title', String(length=80), nullable=False),
    Column('description', Text, nullable=True),
    Column('visibility', String(length=16), nullable=False),
    Column('trip_start', Date, nullable=True),
    Column('trip_end', Date, nullable=True),
    Column('status', String(length=16), nullable=False, server_default=VisitStatus.VISITED),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
    Index('idx_user_id', 'user_id'),
    Index('idx_country_code', 'country_code'),
    Index('idx_visits_visibility', 'visibility'),
)
