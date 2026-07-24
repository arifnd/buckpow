"""add device local_ip

Revision ID: a1b2c3d4e5f6
Revises: b743ebc96c75
Create Date: 2026-07-24 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

revision = 'a1b2c3d4e5f6'
down_revision = 'b743ebc96c75'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('devices', schema=None) as batch_op:
        batch_op.add_column(sa.Column('local_ip', sa.String(length=45), nullable=True))


def downgrade():
    with op.batch_alter_table('devices', schema=None) as batch_op:
        batch_op.drop_column('local_ip')
