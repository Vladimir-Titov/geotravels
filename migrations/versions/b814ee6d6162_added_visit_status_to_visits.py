"""added visit_status to visits

Revision ID: b814ee6d6162
Revises: 97416cb5e0b2
Create Date: 2026-04-22 17:46:28.226611

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b814ee6d6162'
down_revision = '97416cb5e0b2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint('telegram_users_telgram_id_uniq', 'telegram_users', ['telegram_id'], schema='tripmark')
    op.add_column('visits', sa.Column('trip_start', sa.Date(), nullable=True), schema='tripmark')
    op.add_column('visits', sa.Column('trip_end', sa.Date(), nullable=True), schema='tripmark')
    op.add_column(
        'visits', sa.Column('status', sa.String(length=16), server_default='visited', nullable=False), schema='tripmark'
    )


def downgrade() -> None:
    op.drop_column('visits', 'status', schema='tripmark')
    op.drop_column('visits', 'trip_end', schema='tripmark')
    op.drop_column('visits', 'trip_start', schema='tripmark')
    op.drop_constraint(None, 'telegram_users', schema='tripmark', type_='unique')
