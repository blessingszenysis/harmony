"""Add dimensions_values column to alert_definitions table to allow for
dimension value filtering in alerts

Revision ID: 31805c1630cf
Revises: 6722855f6ce5
Create Date: 2020-09-09 17:23:44.082746

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '31805c1630cf'
down_revision = 'e15c910d7f81'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('alert_definitions', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('dimension_values', postgresql.ARRAY(sa.String()), nullable=True)
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('alert_definitions', schema=None) as batch_op:
        batch_op.drop_column('dimension_values')

    # ### end Alembic commands ###
