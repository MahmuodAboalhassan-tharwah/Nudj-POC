"""Create Notification Tables

Revision ID: 005_create_notification_tables
Revises: 004_create_organization_table
Create Date: 2026-02-09 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '005_create_notification_tables'
down_revision: Union[str, None] = '004_create_organization_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create notifications table
    op.create_table('notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('link', sa.String(length=500), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create index on user_id for efficient querying of user notifications
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'], unique=False)

    # Create composite index on user_id and is_read for filtering unread notifications
    op.create_index('ix_notifications_user_read', 'notifications', ['user_id', 'is_read'], unique=False)

    # Create index on created_at for sorting by recency
    op.create_index(op.f('ix_notifications_created_at'), 'notifications', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_notifications_created_at'), table_name='notifications')
    op.drop_index('ix_notifications_user_read', table_name='notifications')
    op.drop_index(op.f('ix_notifications_user_id'), table_name='notifications')

    # Drop notifications table
    op.drop_table('notifications')
