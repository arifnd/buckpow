"""initial models

Revision ID: 6ec5a172b3a6
Revises:
Create Date: 2026-07-08 13:57:44.348640

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6ec5a172b3a6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('email', sa.String(length=256), nullable=False),
        sa.Column('password', sa.String(length=256), nullable=False),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)

    op.create_table('projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('devices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.String(length=64), nullable=False),
        sa.Column('alias', sa.String(length=128), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sampling_interval', sa.Integer(), nullable=True),
        sa.Column('last_seen', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=16), nullable=True),
        sa.Column('api_key', sa.String(length=64), nullable=True),
        sa.Column('firmware_version', sa.String(length=64), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=True),
        sa.Column('high_current_threshold', sa.Float(), nullable=True),
        sa.Column('high_power_threshold', sa.Float(), nullable=True),
        sa.Column('low_voltage_threshold', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('devices', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_devices_device_id'), ['device_id'], unique=True)
        batch_op.create_index(batch_op.f('ix_devices_api_key'), ['api_key'], unique=True)

    op.create_table('sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), sa.ForeignKey('devices.id'), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('target_device', sa.String(length=64), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=16), nullable=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), sa.ForeignKey('devices.id'), nullable=False),
        sa.Column('level', sa.String(length=16), nullable=False, server_default='warning'),
        sa.Column('message', sa.String(length=256), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('alerts', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_alerts_device_id'), ['device_id'])

    op.create_table('measurements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), sa.ForeignKey('sessions.id'), nullable=True),
        sa.Column('device_id', sa.Integer(), sa.ForeignKey('devices.id'), nullable=False),
        sa.Column('bus_voltage', sa.Float(), nullable=False),
        sa.Column('shunt_voltage', sa.Float(), nullable=True),
        sa.Column('load_voltage', sa.Float(), nullable=False),
        sa.Column('current', sa.Float(), nullable=False),
        sa.Column('power', sa.Float(), nullable=False),
        sa.Column('energy', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('measurements', schema=None) as batch_op:
        batch_op.create_index('idx_measurement_device_time', ['device_id', 'created_at'], unique=False)
        batch_op.create_index('idx_measurement_session_time', ['session_id', 'created_at'], unique=False)


def downgrade():
    with op.batch_alter_table('measurements', schema=None) as batch_op:
        batch_op.drop_index('idx_measurement_session_time')
        batch_op.drop_index('idx_measurement_device_time')
    op.drop_table('measurements')

    with op.batch_alter_table('alerts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_alerts_device_id'))
    op.drop_table('alerts')

    op.drop_table('sessions')

    with op.batch_alter_table('devices', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_devices_device_id'))
        batch_op.drop_index(batch_op.f('ix_devices_api_key'))
    op.drop_table('devices')

    op.drop_table('projects')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_email'))
    op.drop_table('users')
