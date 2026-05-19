from sqlalchemy import Column, DateTime, String, Table, Uuid, func

from app.models.base import metadata

achievements = Table(
    'achievements',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('title', String(length=32), nullable=False),
    Column('description', String(length=320), nullable=False),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
    Column('logo_url', String(length=200), nullable=True),
)
