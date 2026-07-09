"""Add api_key to devices

Revision ID: c937257e2e19
Revises: 0a1cba7733dc
Create Date: 2026-07-09 15:29:23.927609

"""
import secrets
from alembic import op
import sqlalchemy as sa


revision = 'c937257e2e19'
down_revision = '0a1cba7733dc'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('devices', schema=None) as batch_op:
        batch_op.add_column(sa.Column('api_key', sa.String(length=64), nullable=True))
        batch_op.create_index(batch_op.f('ix_devices_api_key'), ['api_key'], unique=True)

    conn = op.get_bind()
    devices = conn.execute(sa.text('SELECT id FROM devices WHERE api_key IS NULL')).fetchall()
    for (dev_id,) in devices:
        key = secrets.token_hex(32)
        conn.execute(
            sa.text('UPDATE devices SET api_key = :key WHERE id = :id'),
            {'key': key, 'id': dev_id},
        )


def downgrade():
    with op.batch_alter_table('devices', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_devices_api_key'))
        batch_op.drop_column('api_key')
