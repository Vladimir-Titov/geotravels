from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB

metadata = MetaData(schema='tripmark')

users = Table(
    'users',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('email', String(length=320), nullable=True),
    Column('first_name', String(length=64), nullable=True),
    Column('last_name', String(length=64), nullable=True),
    Column('username', String(length=32), nullable=True),
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
    Column('labels', JSONB(), nullable=True),
    Column('meta', JSONB(), nullable=True),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
)

cities = Table(
    'cities',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column(
        'country_code',
        String(length=2),
        ForeignKey('countries.iso_a2', ondelete='RESTRICT'),
        nullable=False,
    ),
    Column('name', String(length=200), nullable=False),
    Column('name_normalized', String(length=200), nullable=False),
    Column('latitude', Numeric(precision=9, scale=6), nullable=True),
    Column('longitude', Numeric(precision=9, scale=6), nullable=True),
    Column('population', BigInteger(), nullable=True),
    Column('labels', JSONB(), nullable=True),
    Column('meta', JSONB(), nullable=True),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
    Index('idx_cities_country_code', 'country_code'),
    Index('idx_cities_name_normalized', 'name_normalized'),
    Index('idx_cities_country_name', 'country_code', 'name_normalized'),
)

visits = Table(
    'visits',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('user_id', Uuid(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('country_code', String(length=2), ForeignKey('countries.iso_a2', ondelete='RESTRICT'), nullable=False),
    Column('city_id', Uuid(as_uuid=True), ForeignKey('cities.id', ondelete='SET NULL'), nullable=True),
    Column('trip_date', Date, nullable=True),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
    Index('idx_user_id', 'user_id'),
    Index('idx_country_code', 'country_code'),
    Index('idx_city_id', 'city_id'),
)

followers = Table(
    'followers',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('follower_id', Uuid(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('following_id', Uuid(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
    Index('idx_followers_follower_id', 'follower_id'),
    Index('idx_followers_following_id', 'following_id'),
    Index('idx_followers_follower_following_unique', 'follower_id', 'following_id', unique=True),
)

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

users_achievements = Table(
    'users_achievements',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('user_id', Uuid(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column(
        'achievements_id',
        Uuid(as_uuid=True),
        ForeignKey('achievements.id', ondelete='CASCADE'),
        nullable=False,
    ),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
    Column('complete_at', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Index('idx_users_achievements_user_id', 'user_id'),
    Index('idx_users_achievements_achievements_id', 'achievements_id'),
)

files = Table(
    'files',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('file_url', String(length=200), nullable=False),
    Column('filename', String(length=64), nullable=True),
    Column('file_type', String(length=64), nullable=True),
)

files_visits = Table(
    'files_visits',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('file_id', Uuid(as_uuid=True), ForeignKey('files.id', ondelete='SET NULL'), nullable=True),
    Column('visit_id', Uuid(as_uuid=True), ForeignKey('visits.id', ondelete='SET NULL'), nullable=True),
    Column('user_id', Uuid(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
    Column('is_private', Boolean(), nullable=False, server_default='false'),
    Index('idx_files_visits_file_id', 'file_id'),
    Index('idx_files_visits_visit_id', 'visit_id'),
    Index('idx_files_visits_user_id', 'user_id'),
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
