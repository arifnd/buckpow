"""Add project model and project_id to device/session

Revision ID: 0a1cba7733dc
Revises: abc1234
Create Date: 2026-07-09 15:21:06.434428

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a1cba7733dc'
down_revision = 'abc1234'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('devices', schema=None) as batch_op:
        batch_op.add_column(sa.Column('project_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_devices_project_id', 'projects', ['project_id'], ['id'])

    with op.batch_alter_table('sessions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('project_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_sessions_project_id', 'projects', ['project_id'], ['id'])


def downgrade():
    with op.batch_alter_table('sessions', schema=None) as batch_op:
        batch_op.drop_constraint('fk_sessions_project_id', type_='foreignkey')
        batch_op.drop_column('project_id')

    with op.batch_alter_table('devices', schema=None) as batch_op:
        batch_op.drop_constraint('fk_devices_project_id', type_='foreignkey')
        batch_op.drop_column('project_id')
