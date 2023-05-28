"""Add dimension category mapping and
add description to the dimension model

Revision ID: 6b05b608e3b3
Revises: 31805c1630cf
Create Date: 2020-10-06 20:05:21.048937

"""
from alembic import op
import sqlalchemy as sa

# pylint: disable=C0301
# pylint: disable=C0103
# pylint: disable=E1101
# revision identifiers, used by Alembic.
revision = '6b05b608e3b3'
down_revision = '31805c1630cf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'dimension_category_mapping',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dimension_id', sa.String(), nullable=False),
        sa.Column('category_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ['category_id'], ['category.id'], name='valid_category', ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['dimension_id'],
            ['dimension.id'],
            name='valid_dimension',
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('dimension_id', 'category_id'),
    )
    with op.batch_alter_table('dimension', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('description', sa.String(), server_default='', nullable=True)
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('dimension', schema=None) as batch_op:
        batch_op.drop_column('description')

    op.drop_table('dimension_category_mapping')
    # ### end Alembic commands ###
