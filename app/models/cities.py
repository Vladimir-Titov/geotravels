from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Numeric, String, Table, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base import metadata

cities = Table(
    'cities',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('country_code', String(length=2), ForeignKey('countries.iso_a2', ondelete='RESTRICT'), nullable=False),
    Column('name', String(length=200), nullable=False),
    Column('latitude', Numeric(precision=9, scale=6), nullable=True),
    Column('longitude', Numeric(precision=9, scale=6), nullable=True),
    Column('population', BigInteger(), nullable=True),
    Column('labels', JSONB(), nullable=True),
    Column('meta', JSONB(), nullable=True),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
    Index('idx_cities_country_code', 'country_code'),
)
