"""Migration to fix alerts schemas, move `AlertDefinition.checks` to type JSON.

Revision ID: 1b25c9c0b5dc
Revises: 010bef7d6239
Create Date: 2018-05-08 18:00:24.877724

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b25c9c0b5dc'
down_revision = '010bef7d6239'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('alert_definitions', 'checks', type_=sa.JSON(), postgresql_using=('checks::json'))

    with op.batch_alter_table('alert_definitions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('valid_user', 'user', ['user_id'], ['id'])
        batch_op.drop_column('user')

    with op.batch_alter_table('alert_notifications', schema=None) as batch_op:
        batch_op.drop_column('dimension_name')
        batch_op.drop_column('field_id')
        batch_op.drop_column('user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('alert_definitions', 'checks', type_=sa.Text())

    with op.batch_alter_table('alert_notifications', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('field_id', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('dimension_name', sa.VARCHAR(), autoincrement=False, nullable=True))

    with op.batch_alter_table('alert_definitions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.drop_constraint('valid_user', type_='foreignkey')
        batch_op.drop_column('user_id')
    # ### end Alembic commands ###
