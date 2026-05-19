"""refactor visit dates cities and city normalization

Revision ID: 20a54745cd11
Revises: 1b8d6f42a0c7
Create Date: 2026-05-08 09:35:53.553278

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '20a54745cd11'
down_revision = '1b8d6f42a0c7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE tripmark.visits
        SET
            trip_start = COALESCE(date_from, trip_start),
            trip_end = COALESCE(date_to, trip_end),
            title = COALESCE(NULLIF(BTRIM(title), ''), 'Untitled trip'),
            visibility = COALESCE(NULLIF(BTRIM(visibility), ''), 'private')
        """
    )
    op.execute(
        """
        INSERT INTO tripmark.visits_cities (id, visit_id, city_id)
        SELECT uuid_generate_v4(), id, city_id
        FROM tripmark.visits
        WHERE city_id IS NOT NULL
        ON CONFLICT (visit_id, city_id) DO NOTHING
        """
    )

    op.drop_index(op.f('idx_cities_country_name'), table_name='cities', schema='tripmark')
    op.drop_index(op.f('idx_cities_name_normalized'), table_name='cities', schema='tripmark')
    op.drop_column('cities', 'name_normalized', schema='tripmark')
    op.alter_column(
        'visits',
        'title',
        existing_type=sa.VARCHAR(length=80),
        nullable=False,
        schema='tripmark',
    )
    op.alter_column(
        'visits',
        'visibility',
        existing_type=sa.VARCHAR(length=16),
        nullable=False,
        existing_server_default=sa.text("'private'::character varying"),
        schema='tripmark',
    )
    op.drop_index(op.f('idx_city_id'), table_name='visits', schema='tripmark')
    op.drop_constraint(op.f('fk_visits_city_id_cities'), 'visits', schema='tripmark', type_='foreignkey')
    op.drop_column('visits', 'date_to', schema='tripmark')
    op.drop_column('visits', 'date_from', schema='tripmark')
    op.drop_column('visits', 'city_id', schema='tripmark')


def downgrade() -> None:
    op.add_column('visits', sa.Column('city_id', sa.UUID(), autoincrement=False, nullable=True), schema='tripmark')
    op.add_column('visits', sa.Column('date_from', sa.DATE(), autoincrement=False, nullable=True), schema='tripmark')
    op.add_column('visits', sa.Column('date_to', sa.DATE(), autoincrement=False, nullable=True), schema='tripmark')
    op.execute(
        """
        UPDATE tripmark.visits
        SET
            date_from = trip_start,
            date_to = trip_end,
            city_id = (
                SELECT visits_cities.city_id
                FROM tripmark.visits_cities
                WHERE visits_cities.visit_id = visits.id
                ORDER BY visits_cities.created ASC, visits_cities.id ASC
                LIMIT 1
            )
        """
    )
    op.create_foreign_key(
        op.f('fk_visits_city_id_cities'),
        'visits',
        'cities',
        ['city_id'],
        ['id'],
        source_schema='tripmark',
        referent_schema='tripmark',
        ondelete='SET NULL',
    )
    op.create_index(op.f('idx_city_id'), 'visits', ['city_id'], unique=False, schema='tripmark')
    op.alter_column(
        'visits',
        'visibility',
        existing_type=sa.VARCHAR(length=16),
        nullable=True,
        existing_server_default=sa.text("'private'::character varying"),
        schema='tripmark',
    )
    op.alter_column(
        'visits',
        'title',
        existing_type=sa.VARCHAR(length=80),
        nullable=True,
        schema='tripmark',
    )
    op.add_column(
        'cities',
        sa.Column('name_normalized', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
        schema='tripmark',
    )
    op.execute('UPDATE tripmark.cities SET name_normalized = LOWER(name)')
    op.alter_column(
        'cities',
        'name_normalized',
        existing_type=sa.VARCHAR(length=200),
        nullable=False,
        schema='tripmark',
    )
    op.create_index(op.f('idx_cities_name_normalized'), 'cities', ['name_normalized'], unique=False, schema='tripmark')
    op.create_index(
        op.f('idx_cities_country_name'),
        'cities',
        ['country_code', 'name_normalized'],
        unique=False,
        schema='tripmark',
    )
