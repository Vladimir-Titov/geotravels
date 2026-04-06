"""add achievements tables

Revision ID: d4f8e2a1c9b7
Revises: b7f1e6d4a2c9
Create Date: 2026-04-06 19:10:00.000000

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'd4f8e2a1c9b7'
down_revision = 'b7f1e6d4a2c9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'achievements',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=32), nullable=False),
        sa.Column('description', sa.String(length=320), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('logo_url', sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='tripmark',
    )

    op.create_table(
        'users_achievements',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('achievements_id', sa.Uuid(), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('complete_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['achievements_id'], ['tripmark.achievements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['tripmark.users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='tripmark',
    )
    op.create_index(
        'idx_users_achievements_user_id',
        'users_achievements',
        ['user_id'],
        unique=False,
        schema='tripmark',
    )
    op.create_index(
        'idx_users_achievements_achievements_id',
        'users_achievements',
        ['achievements_id'],
        unique=False,
        schema='tripmark',
    )


def downgrade() -> None:
    op.drop_index('idx_users_achievements_achievements_id', table_name='users_achievements', schema='tripmark')
    op.drop_index('idx_users_achievements_user_id', table_name='users_achievements', schema='tripmark')
    op.drop_table('users_achievements', schema='tripmark')
    op.drop_table('achievements', schema='tripmark')
