"""visits story contract v2

Revision ID: a1d2f3c4b5e6
Revises: e1f9a3c6b2d4, f2a5c3d1b8e4
Create Date: 2026-04-21 15:10:00.000000

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'a1d2f3c4b5e6'
down_revision = ('e1f9a3c6b2d4', 'f2a5c3d1b8e4')
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('visits', sa.Column('title', sa.String(length=80), nullable=True), schema='tripmark')
    op.add_column('visits', sa.Column('description', sa.Text(), nullable=True), schema='tripmark')
    op.add_column(
        'visits',
        sa.Column('visibility', sa.String(length=16), nullable=False, server_default=sa.text("'private'")),
        schema='tripmark',
    )
    op.add_column('visits', sa.Column('date_from', sa.Date(), nullable=True), schema='tripmark')
    op.add_column('visits', sa.Column('date_to', sa.Date(), nullable=True), schema='tripmark')
    op.add_column('visits', sa.Column('cover_file_id', sa.Uuid(), nullable=True), schema='tripmark')

    op.execute("UPDATE tripmark.visits SET title = COALESCE(NULLIF(title, ''), 'Untitled story')")
    op.execute('UPDATE tripmark.visits SET date_from = COALESCE(date_from, trip_date, created::date)')

    op.alter_column(
        'visits',
        'title',
        schema='tripmark',
        existing_type=sa.String(length=80),
        nullable=False,
        server_default=sa.text("'Untitled story'"),
    )
    op.alter_column(
        'visits',
        'date_from',
        schema='tripmark',
        existing_type=sa.Date(),
        nullable=False,
        server_default=sa.text('CURRENT_DATE'),
    )

    op.create_foreign_key(
        'fk_visits_cover_file_id_files',
        'visits',
        'files',
        ['cover_file_id'],
        ['id'],
        source_schema='tripmark',
        referent_schema='tripmark',
        ondelete='SET NULL',
    )
    op.create_index('idx_visits_cover_file_id', 'visits', ['cover_file_id'], unique=False, schema='tripmark')
    op.create_index('idx_visits_visibility', 'visits', ['visibility'], unique=False, schema='tripmark')

    op.create_table(
        'visits_cities',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('visit_id', sa.Uuid(), nullable=False),
        sa.Column('city_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['visit_id'], ['tripmark.visits.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['city_id'], ['tripmark.cities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='tripmark',
    )
    op.create_index('idx_visits_cities_visit_id', 'visits_cities', ['visit_id'], unique=False, schema='tripmark')
    op.create_index('idx_visits_cities_city_id', 'visits_cities', ['city_id'], unique=False, schema='tripmark')
    op.create_index(
        'idx_visits_cities_visit_city_unique',
        'visits_cities',
        ['visit_id', 'city_id'],
        unique=True,
        schema='tripmark',
    )

    op.execute(
        """
        INSERT INTO tripmark.visits_cities (id, visit_id, city_id)
        SELECT
            (
                substr(md5(v.id::text || v.city_id::text), 1, 8) || '-' ||
                substr(md5(v.id::text || v.city_id::text), 9, 4) || '-' ||
                substr(md5(v.id::text || v.city_id::text), 13, 4) || '-' ||
                substr(md5(v.id::text || v.city_id::text), 17, 4) || '-' ||
                substr(md5(v.id::text || v.city_id::text), 21, 12)
            )::uuid,
            v.id,
            v.city_id
        FROM tripmark.visits v
        WHERE v.city_id IS NOT NULL
        ON CONFLICT (visit_id, city_id) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_index('idx_visits_cities_visit_city_unique', table_name='visits_cities', schema='tripmark')
    op.drop_index('idx_visits_cities_city_id', table_name='visits_cities', schema='tripmark')
    op.drop_index('idx_visits_cities_visit_id', table_name='visits_cities', schema='tripmark')
    op.drop_table('visits_cities', schema='tripmark')

    op.drop_index('idx_visits_visibility', table_name='visits', schema='tripmark')
    op.drop_index('idx_visits_cover_file_id', table_name='visits', schema='tripmark')
    op.drop_constraint('fk_visits_cover_file_id_files', 'visits', schema='tripmark', type_='foreignkey')

    op.drop_column('visits', 'cover_file_id', schema='tripmark')
    op.drop_column('visits', 'date_to', schema='tripmark')
    op.drop_column('visits', 'date_from', schema='tripmark')
    op.drop_column('visits', 'visibility', schema='tripmark')
    op.drop_column('visits', 'description', schema='tripmark')
    op.drop_column('visits', 'title', schema='tripmark')
