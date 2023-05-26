"""Add created field on user model

Revision ID: 853e0e8aa6a0
Revises: e92d061b0bfc
Create Date: 2019-09-20 00:07:40.125825

"""
from alembic import op
import sqlalchemy as sa

# pylint: disable=C0301
# pylint: disable=C0103
# pylint: disable=E1101
# revision identifiers, used by Alembic.
revision = '853e0e8aa6a0'
down_revision = 'e92d061b0bfc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('created')
    # ### end Alembic commands ###