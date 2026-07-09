"""add user model

Revision ID: abc1234
Revises: 6ec5a172b3a6
Create Date: 2026-07-09 14:57:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'abc1234'
down_revision = '6ec5a172b3a6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('email', sa.String(length=256), nullable=False),
        sa.Column('password', sa.String(length=256), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_email'))
    op.drop_table('users')
