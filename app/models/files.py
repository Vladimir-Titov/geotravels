from enum import StrEnum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, Table, Uuid, func

from app.models.base import metadata


class FileVisibility(StrEnum):
    PRIVATE = 'private'
    FOLLOWERS = 'followers'
    PUBLIC = 'public'


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
