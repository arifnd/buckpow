"""Add alerts table

Revision ID: 1b277661dc3b
Revises: fae56d96855c
Create Date: 2026-07-09 15:42:13.967519

"""
from alembic import op
from alembic.migration import MigrationContext
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b277661dc3b'
down_revision = 'fae56d96855c'
branch_labels = None
depends_on = None


def upgrade():
    ctx = op.get_context()
    if ctx.dialect.has_table(ctx.connection, 'alerts'):
        return
    op.create_table(
        'alerts',
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


def downgrade():
    with op.batch_alter_table('alerts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_alerts_device_id'))
    op.drop_table('alerts')
