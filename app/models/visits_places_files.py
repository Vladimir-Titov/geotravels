from sqlalchemy import Column, DateTime, ForeignKey, Index, Table, Uuid, func

from app.models.base import metadata

visits_places_files = Table(
    'visits_places_files',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('visit_place_id', Uuid(as_uuid=True), ForeignKey('visits_places.id', ondelete='CASCADE'), nullable=False),
    Column('file_id', Uuid(as_uuid=True), ForeignKey('files.id', ondelete='CASCADE'), nullable=False),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
    Index('idx_visits_places_files_visit_place_id', 'visit_place_id'),
    Index('idx_visits_places_files_file_id', 'file_id'),
    Index('idx_visits_places_files_visit_place_file_unique', 'visit_place_id', 'file_id', unique=True),
)
