from sqlalchemy import Column, DateTime, ForeignKey, Index, Table, Uuid, func

from app.models.base import metadata

users_achievements = Table(
    'users_achievements',
    metadata,
    Column('id', Uuid(as_uuid=True), primary_key=True),
    Column('user_id', Uuid(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('achievements_id', Uuid(as_uuid=True), ForeignKey('achievements.id', ondelete='CASCADE'), nullable=False),
    Column('created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('updated', DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()),
    Column('complete_at', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Index('idx_users_achievements_user_id', 'user_id'),
    Index('idx_users_achievements_achievements_id', 'achievements_id'),
)
