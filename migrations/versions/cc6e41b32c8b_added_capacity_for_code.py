"""added capacity for code

Revision ID: cc6e41b32c8b
Revises: a8f2c1d3e7b9
Create Date: 2026-03-22 14:14:28.516022

"""

from __future__ import annotations

import hashlib

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'cc6e41b32c8b'
down_revision = 'a8f2c1d3e7b9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    otp_requests = sa.table(
        'otp_requests',
        sa.column('id', sa.Uuid()),
        sa.column('code', sa.String(length=16)),
        sa.column('code_hash', sa.String(length=64)),
        schema='tripmark',
    )

    op.add_column('otp_requests', sa.Column('code_hash', sa.String(length=64), nullable=True), schema='tripmark')
    op.add_column(
        'otp_requests',
        sa.Column('status', sa.String(length=20), nullable=False, server_default='sent'),
        schema='tripmark',
    )

    bind = op.get_bind()
    rows = bind.execute(sa.select(otp_requests.c.id, otp_requests.c.code)).fetchall()
    for row in rows:
        hashed = hashlib.sha256(row.code.encode()).hexdigest()
        bind.execute(
            otp_requests.update().where(otp_requests.c.id == row.id).values(code_hash=hashed),
        )

    op.alter_column('otp_requests', 'code_hash', nullable=False, schema='tripmark')
    op.drop_column('otp_requests', 'code', schema='tripmark')


def downgrade() -> None:
    op.add_column(
        'otp_requests',
        sa.Column('code', sa.VARCHAR(length=16), autoincrement=False, nullable=False, server_default='000000'),
        schema='tripmark',
    )
    op.drop_column('otp_requests', 'code_hash', schema='tripmark')
    op.drop_column('otp_requests', 'status', schema='tripmark')
    op.alter_column('otp_requests', 'code', server_default=None, schema='tripmark')
