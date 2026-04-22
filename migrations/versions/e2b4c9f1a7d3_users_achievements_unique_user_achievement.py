"""users achievements unique user achievement

Revision ID: e2b4c9f1a7d3
Revises: dc75048e7837
Create Date: 2026-04-22 00:00:00.000000

"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = 'e2b4c9f1a7d3'
down_revision = 'dc75048e7837'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        'idx_users_achievements_user_achievement_unique',
        'users_achievements',
        ['user_id', 'achievements_id'],
        unique=True,
        schema='tripmark',
    )


def downgrade() -> None:
    op.drop_index(
        'idx_users_achievements_user_achievement_unique',
        table_name='users_achievements',
        schema='tripmark',
    )
