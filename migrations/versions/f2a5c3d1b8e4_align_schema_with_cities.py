"""align schema with cities

Revision ID: f2a5c3d1b8e4
Revises: cc6e41b32c8b
Create Date: 2026-04-05 18:00:00.000000

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = 'f2a5c3d1b8e4'
down_revision = 'cc6e41b32c8b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('first_name', sa.String(length=64), nullable=True), schema='tripmark')
    op.add_column('users', sa.Column('last_name', sa.String(length=64), nullable=True), schema='tripmark')
    op.add_column('users', sa.Column('username', sa.String(length=32), nullable=True), schema='tripmark')

    op.add_column('countries', sa.Column('labels', JSONB(), nullable=True), schema='tripmark')
    op.add_column('countries', sa.Column('meta', JSONB(), nullable=True), schema='tripmark')

    op.create_table(
        'cities',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('country_code', sa.String(length=2), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('name_normalized', sa.String(length=200), nullable=False),
        sa.Column('latitude', sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column('population', sa.BigInteger(), nullable=True),
        sa.Column('labels', JSONB(), nullable=True),
        sa.Column('meta', JSONB(), nullable=True),
        sa.Column('created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['country_code'], ['tripmark.countries.iso_a2'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        schema='tripmark',
    )
    op.create_index('idx_cities_country_code', 'cities', ['country_code'], unique=False, schema='tripmark')
    op.create_index('idx_cities_name_normalized', 'cities', ['name_normalized'], unique=False, schema='tripmark')
    op.create_index(
        'idx_cities_country_name',
        'cities',
        ['country_code', 'name_normalized'],
        unique=False,
        schema='tripmark',
    )

    op.add_column('visits', sa.Column('city_id', sa.Uuid(), nullable=True), schema='tripmark')
    op.create_foreign_key(
        'fk_visits_city_id_cities',
        'visits',
        'cities',
        ['city_id'],
        ['id'],
        source_schema='tripmark',
        referent_schema='tripmark',
        ondelete='SET NULL',
    )
    op.create_index('idx_city_id', 'visits', ['city_id'], unique=False, schema='tripmark')
    op.drop_column('visits', 'marked_at', schema='tripmark')


def downgrade() -> None:
    op.add_column(
        'visits',
        sa.Column('marked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        schema='tripmark',
    )
    op.drop_index('idx_city_id', table_name='visits', schema='tripmark')
    op.drop_constraint('fk_visits_city_id_cities', 'visits', schema='tripmark', type_='foreignkey')
    op.drop_column('visits', 'city_id', schema='tripmark')

    op.drop_index('idx_cities_country_name', table_name='cities', schema='tripmark')
    op.drop_index('idx_cities_name_normalized', table_name='cities', schema='tripmark')
    op.drop_index('idx_cities_country_code', table_name='cities', schema='tripmark')
    op.drop_table('cities', schema='tripmark')

    op.drop_column('countries', 'meta', schema='tripmark')
    op.drop_column('countries', 'labels', schema='tripmark')

    op.drop_column('users', 'username', schema='tripmark')
    op.drop_column('users', 'last_name', schema='tripmark')
    op.drop_column('users', 'first_name', schema='tripmark')
