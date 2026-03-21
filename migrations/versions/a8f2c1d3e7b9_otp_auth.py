"""otp auth

Revision ID: a8f2c1d3e7b9
Revises: 3f3f014f9299
Create Date: 2026-03-21 00:00:00.000000

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'a8f2c1d3e7b9'
down_revision = '3f3f014f9299'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('users', 'password_hash', schema='tripmark')
    op.create_table(
        'otp_requests',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('contact', sa.String(length=320), nullable=False),
        sa.Column('code', sa.String(length=16), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('attempts', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='tripmark',
    )


def downgrade() -> None:
    op.drop_table('otp_requests', schema='tripmark')
    op.add_column('users', sa.Column('password_hash', sa.String(length=64), nullable=True), schema='tripmark')
