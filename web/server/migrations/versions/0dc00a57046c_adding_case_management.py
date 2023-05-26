# pylint: disable=C0103
"""
Moves case management information to the backend

New tables:
case_metadata_type
case_status_type
case_type
case_type_default_druid_dimension
case_type_default_field
case_type_default_metadata
case_type_default_status
external_alert_type
external_alert_activity_to_ignore

Revision ID: 0dc00a57046c
Revises: 213b541d942f
Create Date: 2019-07-12 12:04:17.991656

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import ENUM

# revision identifiers, used by Alembic.
revision = '0dc00a57046c'
down_revision = '213b541d942f'
branch_labels = None
depends_on = None

metadata_type_enum = ENUM(
    'STRING',
    'PHONE_NUMBER',
    'NUMBER',
    'DATE',
    name='metadata_type_enum',
    create_type=False,
)
case_type_enum = ENUM('ALERT', 'DRUID', name='case_type_enum', create_type=False)


# pylint: disable=E1101
def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Create the enums
    metadata_type_enum.create(op.get_bind(), checkfirst=True)
    case_type_enum.create(op.get_bind(), checkfirst=True)

    # Create the tables
    op.create_table(
        'case_metadata_type',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('type', metadata_type_enum, nullable=False),
        sa.Column('is_editable', sa.Boolean(), nullable=False),
        sa.Column('is_displayed_empty', sa.Boolean(), nullable=False),
        sa.Column('empty_display_value', sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'case_status_type',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('is_open', sa.Boolean(), nullable=True),
        sa.Column('is_new', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'case_type',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', case_type_enum, nullable=False),
        sa.Column('druid_dimension', sa.Text(), nullable=True),
        sa.Column('default_case_status_type_id', sa.Integer(), nullable=False),
        sa.Column('is_metadata_expandable', sa.Boolean(), nullable=False),
        sa.Column('can_users_add_events', sa.Boolean(), nullable=False),
        sa.Column(
            'default_dashboard_queries',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column('spec', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(
            ['default_case_status_type_id'],
            ['case_status_type.id'],
            name='valid_default_case_status_type',
            onupdate='CASCADE',
            ondelete='RESTRICT',
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('druid_dimension'),
    )
    op.create_table(
        'case_type_default_druid_dimension',
        sa.Column('case_type_id', sa.Integer(), nullable=False),
        sa.Column('druid_dimension_name', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ['case_type_id'],
            ['case_type.id'],
            name='valid_case_type',
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('case_type_id', 'druid_dimension_name'),
    )
    op.create_table(
        'case_type_default_field',
        sa.Column('case_type_id', sa.Integer(), nullable=False),
        sa.Column('field_id', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ['case_type_id'],
            ['case_type.id'],
            name='valid_case_type',
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('case_type_id', 'field_id'),
    )
    op.create_table(
        'case_type_default_metadata',
        sa.Column('case_type_id', sa.Integer(), nullable=False),
        sa.Column('case_metadata_type_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['case_metadata_type_id'],
            ['case_metadata_type.id'],
            name='valid_case_metadata_type',
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['case_type_id'],
            ['case_type.id'],
            name='valid_case_type',
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('case_type_id', 'case_metadata_type_id'),
    )
    op.create_table(
        'case_type_default_status',
        sa.Column('case_type_id', sa.Integer(), nullable=False),
        sa.Column('case_status_type_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['case_status_type_id'],
            ['case_status_type.id'],
            name='case_status_type',
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['case_type_id'],
            ['case_type.id'],
            name='valid_case_type',
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('case_type_id', 'case_status_type_id'),
    )
    op.create_table(
        'external_alert_type',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('case_type_id', sa.Integer(), nullable=False),
        sa.Column('field_id', sa.Text(), nullable=False),
        sa.Column('druid_dimension', sa.Text(), nullable=False),
        sa.Column('data_dimension', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ['case_type_id'],
            ['case_type.id'],
            name='valid_case_type',
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_table(
        'external_alert_activity_to_ignore',
        sa.Column('external_alert_type_id', sa.Integer(), nullable=False),
        sa.Column('activity', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ['external_alert_type_id'],
            ['external_alert_type.id'],
            name='valid_external_alert_type',
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('external_alert_type_id', 'activity'),
    )

    # Old change that was never migrated
    with op.batch_alter_table('alert_definitions', schema=None) as batch_op:
        batch_op.alter_column(
            'authorization_resource_id', existing_type=sa.INTEGER(), nullable=False
        )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Undoing old change that was never migrated
    with op.batch_alter_table('alert_definitions', schema=None) as batch_op:
        batch_op.alter_column(
            'authorization_resource_id', existing_type=sa.INTEGER(), nullable=True
        )

    # Drop all the new tables
    op.drop_table('external_alert_activity_to_ignore')
    op.drop_table('external_alert_type')
    op.drop_table('case_type_default_status')
    op.drop_table('case_type_default_metadata')
    op.drop_table('case_type_default_field')
    op.drop_table('case_type_default_druid_dimension')
    op.drop_table('case_type')
    op.drop_table('case_status_type')
    op.drop_table('case_metadata_type')

    # Drop the enums
    case_type_enum.drop(op.get_bind(), checkfirst=True)
    metadata_type_enum.drop(op.get_bind(), checkfirst=True)
    # ### end Alembic commands ###
