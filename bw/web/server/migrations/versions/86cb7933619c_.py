"""empty message

Revision ID: 86cb7933619c
Revises: be6b1d1a30d2
Create Date: 2020-05-21 10:51:06.808434

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '86cb7933619c'
down_revision = 'be6b1d1a30d2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table(
        'case_type_default_druid_dimension', schema=None
    ) as batch_op:
        batch_op.add_column(
            sa.Column('show_in_overview_table', sa.Boolean(), nullable=True)
        )

    op.execute(
        'UPDATE case_type_default_druid_dimension SET show_in_overview_table=true'
    )
    op.alter_column(
        'case_type_default_druid_dimension', 'show_in_overview_table', nullable=False
    )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table(
        'case_type_default_druid_dimension', schema=None
    ) as batch_op:
        batch_op.drop_column('show_in_overview_table')

    # ### end Alembic commands ###
