"""Add threshold columns to device

Revision ID: 2052b3df0b39
Revises: 1b277661dc3b
Create Date: 2026-07-09 15:46:10.165498

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2052b3df0b39'
down_revision = '1b277661dc3b'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('devices', schema=None) as batch_op:
        batch_op.add_column(sa.Column('high_current_threshold', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('high_power_threshold', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('low_voltage_threshold', sa.Float(), nullable=True))


def downgrade():
    with op.batch_alter_table('devices', schema=None) as batch_op:
        batch_op.drop_column('high_current_threshold')
        batch_op.drop_column('high_power_threshold')
        batch_op.drop_column('low_voltage_threshold')
