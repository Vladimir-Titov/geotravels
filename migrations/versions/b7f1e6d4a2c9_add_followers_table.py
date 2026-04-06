"""add followers table

Revision ID: b7f1e6d4a2c9
Revises: f2a5c3d1b8e4
Create Date: 2026-04-06 15:10:00.000000

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'b7f1e6d4a2c9'
down_revision = 'f2a5c3d1b8e4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'followers',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('follower_id', sa.Uuid(), nullable=False),
        sa.Column('following_id', sa.Uuid(), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['follower_id'], ['tripmark.users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['following_id'], ['tripmark.users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='tripmark',
    )
    op.create_index('idx_followers_follower_id', 'followers', ['follower_id'], unique=False, schema='tripmark')
    op.create_index('idx_followers_following_id', 'followers', ['following_id'], unique=False, schema='tripmark')
    op.create_index(
        'idx_followers_follower_following_unique',
        'followers',
        ['follower_id', 'following_id'],
        unique=True,
        schema='tripmark',
    )


def downgrade() -> None:
    op.drop_index('idx_followers_follower_following_unique', table_name='followers', schema='tripmark')
    op.drop_index('idx_followers_following_id', table_name='followers', schema='tripmark')
    op.drop_index('idx_followers_follower_id', table_name='followers', schema='tripmark')
    op.drop_table('followers', schema='tripmark')
