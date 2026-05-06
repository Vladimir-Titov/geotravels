from enum import StrEnum

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
    Text,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB

metadata = MetaData(schema='tripmark')


class VisitStatus(StrEnum):
    PLANNED = 'planned'
    IN_TRIP = 'in_trip'
    VISITED = 'visited'


class VisitVisibility(StrEnum):
    PRIVATE = 'private'
    FOLLOWERS = 'followers'
    PUBLIC = 'public'


class FileVisibility(StrEnum):
    PRIVATE = 'private'
    FOLLOWERS = 'followers'
    PUBLIC = 'public'


class CheckListStatus(StrEnum):
    TO_DO = 'to_do'
    DONE = 'done'


class OtpRequestStatus(StrEnum):
    SENT = 'sent'
    FAILED = 'failed'
    DONE = 'done'


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

visits_checklist = Table(
    'visits_checklist',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('visit_id', Uuid(as_uuid=True), ForeignKey('visits.id', ondelete='CASCADE'), nullable=False),
    Column('content', Text, nullable=False),
    Column('status', String(length=16), nullable=False, server_default=CheckListStatus.TO_DO),
    Column('user_id', Uuid(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
    Index('idx_visits_checklist_visit_id', 'visit_id'),
)

visits_places = Table(
    'visits_places',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('visit_id', Uuid(as_uuid=True), ForeignKey('visits.id', ondelete='CASCADE'), nullable=False),
    Column('title', String(length=255), nullable=False),
    Column('user_id', Uuid(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('is_visited', Boolean, nullable=False, server_default='false'),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
    Index('idx_visits_places_visit_id', 'visit_id'),
    Index('idx_visits_places_visit_title_unique', 'visit_id', 'title', unique=True),
)

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
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
)

files_visits = Table(
    'files_visits',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('file_id', Uuid(as_uuid=True), ForeignKey('files.id', ondelete='SET NULL'), nullable=True),
    Column('visit_id', Uuid(as_uuid=True), ForeignKey('visits.id', ondelete='SET NULL'), nullable=True),
    Column('user_id', Uuid(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
    Column('is_private', Boolean(), nullable=False, server_default='false'),
    Column('is_cover', Boolean(), nullable=False, server_default='false'),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
    Column('visibility', String(length=16), nullable=False),
    Index('idx_files_visits_file_id', 'file_id'),
    Index('idx_files_visits_visit_id', 'visit_id'),
    Index('idx_files_visits_user_id', 'user_id'),
    Index('idx_files_visits_is_cover', 'is_cover'),
    Index(
        'idx_files_visits_cover_unique',
        'visit_id',
        unique=True,
        postgresql_where=(Column('is_cover').is_(True) & Column('visit_id').is_not(None)),
    ),
)

otp_requests = Table(
    'otp_requests',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('contact', String(length=320), nullable=False),
    Column('code_hash', String(length=64), nullable=False),
    Column('expires_at', DateTime(timezone=True), nullable=False),
    Column('attempts', Integer(), nullable=False, server_default='0'),
    Column('status', String(length=20), nullable=False, server_default=OtpRequestStatus.SENT),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
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
