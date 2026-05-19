from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, Table, Uuid, func
from sqlalchemy.sql import false

from app.models.base import metadata

visits_places = Table(
    'visits_places',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('visit_id', Uuid(as_uuid=True), ForeignKey('visits.id', ondelete='CASCADE'), nullable=False),
    Column('title', String(length=255), nullable=False),
    Column('user_id', Uuid(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('is_visited', Boolean, nullable=False, server_default=false()),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
    Index('idx_visits_places_visit_id', 'visit_id'),
    Index('idx_visits_places_visit_title_unique', 'visit_id', 'title', unique=True),
)
