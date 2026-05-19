"""add yandex auth

Revision ID: e91c0a4d7f62
Revises: c76643fb40c6
Create Date: 2026-05-19 16:30:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'e91c0a4d7f62'
down_revision = 'c76643fb40c6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'yandex_users',
        sa.Column('yandex_id', sa.String(length=64), nullable=False),
        sa.Column('login', sa.String(length=255), nullable=True),
        sa.Column('default_email', sa.String(length=320), nullable=True),
        sa.Column('first_name', sa.String(length=64), nullable=True),
        sa.Column('last_name', sa.String(length=64), nullable=True),
        sa.Column('display_name', sa.String(length=255), nullable=True),
        sa.Column('real_name', sa.String(length=255), nullable=True),
        sa.Column('default_avatar_id', sa.String(length=128), nullable=True),
        sa.Column('client_id', sa.String(length=128), nullable=True),
        sa.Column('psuid', sa.String(length=255), nullable=True),
        sa.Column('created', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('yandex_id'),
        sa.UniqueConstraint('yandex_id'),
        schema='tripmark',
    )
    op.add_column('users', sa.Column('yandex_user_id', sa.String(length=64), nullable=True), schema='tripmark')
    op.create_foreign_key(
        'fk_users_yandex_user_id_yandex_users',
        'users',
        'yandex_users',
        ['yandex_user_id'],
        ['yandex_id'],
        source_schema='tripmark',
        referent_schema='tripmark',
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_users_yandex_user_id_yandex_users', 'users', schema='tripmark', type_='foreignkey')
    op.drop_column('users', 'yandex_user_id', schema='tripmark')
    op.drop_table('yandex_users', schema='tripmark')
