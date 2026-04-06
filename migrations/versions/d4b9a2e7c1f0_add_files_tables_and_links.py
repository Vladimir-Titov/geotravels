"""add files tables and links

Revision ID: d4b9a2e7c1f0
Revises: b7f1e6d4a2c9
Create Date: 2026-04-06 18:55:00.000000

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'd4b9a2e7c1f0'
down_revision = 'b7f1e6d4a2c9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'files',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('file_url', sa.String(length=200), nullable=False),
        sa.Column('filename', sa.String(length=64), nullable=True),
        sa.Column('file_type', sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='tripmark',
    )

    op.create_table(
        'files_visits',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('file_id', sa.Uuid(), nullable=True),
        sa.Column('visit_id', sa.Uuid(), nullable=True),
        sa.Column('user_id', sa.Uuid(), nullable=True),
        sa.Column('is_private', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.ForeignKeyConstraint(['file_id'], ['tripmark.files.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['visit_id'], ['tripmark.visits.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['tripmark.users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        schema='tripmark',
    )

    op.create_index('idx_files_visits_file_id', 'files_visits', ['file_id'], unique=False, schema='tripmark')
    op.create_index('idx_files_visits_visit_id', 'files_visits', ['visit_id'], unique=False, schema='tripmark')
    op.create_index('idx_files_visits_user_id', 'files_visits', ['user_id'], unique=False, schema='tripmark')


def downgrade() -> None:
    op.drop_index('idx_files_visits_user_id', table_name='files_visits', schema='tripmark')
    op.drop_index('idx_files_visits_visit_id', table_name='files_visits', schema='tripmark')
    op.drop_index('idx_files_visits_file_id', table_name='files_visits', schema='tripmark')
    op.drop_table('files_visits', schema='tripmark')
    op.drop_table('files', schema='tripmark')
