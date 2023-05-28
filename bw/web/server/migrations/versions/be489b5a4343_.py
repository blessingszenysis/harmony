'''Introduce SA Models for Dynamic Configuration

Revision ID: be489b5a4343
Revises: 9a628ffd6795
Create Date: 2018-01-17 11:54:57.488503

'''
from alembic import op
import sqlalchemy as sa

from web.server.migrations.seed_scripts.seed_be489b58a4343 import add_seed_data, rollback_seed_data

# revision identifiers, used by Alembic.
revision = 'be489b5a4343'
down_revision = '9a628ffd6795'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('configuration',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('key', sa.String(length=100), nullable=False),
                    sa.Column('value', sa.Text(), nullable=True),
                    sa.Column('description', sa.String(), nullable=False),
                    sa.Column('enabled', sa.Boolean(), server_default='0', nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('key')
    )
    # ### end Alembic commands ###
    add_seed_data(op)

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('configuration')
    # ### end Alembic commands ###
    rollback_seed_data(op)
