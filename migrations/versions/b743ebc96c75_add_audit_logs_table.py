"""add audit_logs table

Revision ID: b743ebc96c75
Revises: 6ec5a172b3a6
Create Date: 2026-07-11 00:13:17.752667

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b743ebc96c75'
down_revision = '6ec5a172b3a6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True, index=True),
        sa.Column('action', sa.String(64), nullable=False),
        sa.Column('target_type', sa.String(32), nullable=True),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_audit_created', 'audit_logs', ['created_at'])
    op.create_index('idx_audit_action', 'audit_logs', ['action'])


def downgrade():
    op.drop_index('idx_audit_action', table_name='audit_logs')
    op.drop_index('idx_audit_created', table_name='audit_logs')
    op.drop_table('audit_logs')
