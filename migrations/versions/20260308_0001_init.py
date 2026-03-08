"""initial schema

Revision ID: 20260308_0001
Revises:
Create Date: 2026-03-08 00:00:00.000000

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '20260308_0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('password_hash', sa.String(length=64), nullable=False),
        sa.Column(
            'created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )

    op.create_table(
        'countries',
        sa.Column('iso_a2', sa.String(length=2), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.PrimaryKeyConstraint('iso_a2'),
    )

    op.create_table(
        'visits',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('country_code', sa.String(length=2), nullable=False),
        sa.Column('marked_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('trip_date', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['country_code'], ['countries.iso_a2'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_index('ix_visits_country_code', 'visits', ['country_code'], unique=False)
    op.create_index('ix_visits_user_id', 'visits', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_visits_user_id', table_name='visits')
    op.drop_index('ix_visits_country_code', table_name='visits')
    op.drop_table('visits')
    op.drop_table('countries')
    op.drop_table('users')
