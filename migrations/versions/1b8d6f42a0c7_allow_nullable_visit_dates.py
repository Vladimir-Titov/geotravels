"""allow nullable visit dates

Revision ID: 1b8d6f42a0c7
Revises: d5680011ca31
Create Date: 2026-04-24 12:00:00.000000

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '1b8d6f42a0c7'
down_revision = 'd5680011ca31'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        'visits',
        'date_from',
        schema='tripmark',
        existing_type=sa.Date(),
        nullable=True,
        server_default=None,
    )


def downgrade() -> None:
    op.execute("UPDATE tripmark.visits SET date_from = CURRENT_DATE WHERE date_from IS NULL")
    op.alter_column(
        'visits',
        'date_from',
        schema='tripmark',
        existing_type=sa.Date(),
        nullable=False,
        server_default=sa.text('CURRENT_DATE'),
    )
