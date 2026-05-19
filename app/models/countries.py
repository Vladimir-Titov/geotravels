from sqlalchemy import Column, DateTime, String, Table, func
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base import metadata

countries = Table(
    'countries',
    metadata,
    Column('iso_a2', String(length=2), primary_key=True),
    Column('name', String(length=128), nullable=False),
    Column('labels', JSONB(), nullable=True),
    Column('meta', JSONB(), nullable=True),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
)
