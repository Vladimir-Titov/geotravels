from sqlalchemy import Column, DateTime, ForeignKey, Index, Table, Uuid, func

from app.models.base import metadata

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
