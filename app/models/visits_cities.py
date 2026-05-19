from sqlalchemy import Column, DateTime, ForeignKey, Index, Table, Uuid, func

from app.models.base import metadata

visits_cities = Table(
    'visits_cities',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('visit_id', Uuid(as_uuid=True), ForeignKey('visits.id', ondelete='CASCADE'), nullable=False),
    Column('city_id', Uuid(as_uuid=True), ForeignKey('cities.id', ondelete='CASCADE'), nullable=False),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
    Index('idx_visits_cities_visit_id', 'visit_id'),
    Index('idx_visits_cities_city_id', 'city_id'),
    Index('idx_visits_cities_visit_city_unique', 'visit_id', 'city_id', unique=True),
)
