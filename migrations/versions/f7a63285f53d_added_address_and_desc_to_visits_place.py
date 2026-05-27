"""added address and desc to visits_place

Revision ID: f7a63285f53d
Revises: e91c0a4d7f62
Create Date: 2026-05-27 18:00:14.395550

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7a63285f53d'
down_revision = 'e91c0a4d7f62'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('visits_places', sa.Column('address', sa.Text(), nullable=True), schema='tripmark')
    op.add_column('visits_places', sa.Column('description', sa.Text(), nullable=True), schema='tripmark')


def downgrade() -> None:
    op.drop_column('visits_places', 'description', schema='tripmark')
    op.drop_column('visits_places', 'address', schema='tripmark')

