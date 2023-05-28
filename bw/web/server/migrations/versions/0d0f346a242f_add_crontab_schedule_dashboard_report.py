# pylint: disable=C0301
"""Add crontabSchedule, SchedulerEntry, DashboardReportSchedule

Revision ID: 0d0f346a242f
Revises: de78dcd90eb3
Create Date: 2020-05-28 04:21:16.286187

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# pylint: disable=C0103
# pylint: disable=E1101
# revision identifiers, used by Alembic.
revision = '0d0f346a242f'
down_revision = 'de78dcd90eb3'
branch_labels = None
depends_on = None

schedule_cadence_enum = postgresql.ENUM(
    'DAILY',
    'WEEKLY',
    'MONTHLY',
    'YEARLY',
    name='schedule_cadence_enum',
    create_type=False,
)


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Add enum
    schedule_cadence_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'crontab_schedule',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('minute', sa.String(length=2), nullable=True),
        sa.Column('hour', sa.String(length=2), nullable=True),
        sa.Column('day_of_week', sa.String(length=2), nullable=True),
        sa.Column('day_of_month', sa.String(length=2), nullable=True),
        sa.Column('month_of_year', sa.String(length=2), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'scheduler_entry',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('task', sa.String(length=255), nullable=True),
        sa.Column('crontab_id', sa.Integer(), nullable=True),
        sa.Column('arguments', sa.Text(), nullable=True),
        sa.Column('keyword_arguments', sa.Text(), nullable=True),
        sa.Column('queue', sa.Text(), nullable=True),
        sa.Column('exchange', sa.Text(), nullable=True),
        sa.Column('routing_key', sa.Text(), nullable=True),
        sa.Column('expires', sa.DateTime(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('last_run_at', sa.DateTime(), nullable=True),
        sa.Column('total_run_count', sa.Integer(), nullable=True),
        sa.Column('date_changed', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ['crontab_id'],
            ['crontab_schedule.id'],
            name='valid_crontab',
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_table(
        'dashboard_report_schedule',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dashboard_id', sa.Integer(), nullable=False),
        sa.Column('scheduler_entry_id', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('cadence', schedule_cadence_enum, nullable=False),
        sa.Column('day_offset', sa.Integer(), nullable=True),
        sa.Column('month', sa.String(), nullable=True),
        sa.Column('time_of_day', sa.String(), nullable=True),
        sa.Column('recipients', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('subject', sa.String(length=100), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('should_attach_pdf', sa.Boolean(), nullable=True),
        sa.Column('should_embed_image', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ['dashboard_id'],
            ['dashboard.id'],
            name='valid_dashboard_report_schedule',
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['owner_id'], ['user.id'], name='valid_owner', ondelete='RESTRICT'
        ),
        sa.ForeignKeyConstraint(
            ['scheduler_entry_id'],
            ['scheduler_entry.id'],
            name='valid_scheduler_entry',
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id'),
    )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('dashboard_report_schedule')
    op.drop_table('scheduler_entry')
    op.drop_table('crontab_schedule')
    # Drop the enum
    schedule_cadence_enum.drop(op.get_bind(), checkfirst=True)
    # ### end Alembic commands ###
