"""Create Audit Log Table

Revision ID: 002_create_audit_log_table
Revises: 001_create_auth_tables
Create Date: 2026-02-09 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_create_audit_log_table'
down_revision: Union[str, None] = '001_create_auth_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create AuditEventType enum
    op.execute("""
        CREATE TYPE auditeventtype AS ENUM (
            'login_success', 'login_failed', 'logout',
            'password_changed', 'password_reset_requested', 'password_reset_completed',
            'mfa_enabled', 'mfa_disabled', 'mfa_verified', 'mfa_failed',
            'user_registered', 'role_changed', 'user_deactivated', 'user_reactivated',
            'invitation_sent', 'invitation_accepted', 'invitation_expired', 'invitation_resent',
            'session_created', 'session_expired', 'session_revoked',
            'unauthorized_access', 'account_locked', 'account_unlocked', 'rate_limit_exceeded',
            'data_export_requested', 'data_export_completed', 'data_deletion_requested', 'data_deletion_completed',
            'sso_login_initiated', 'sso_login_success', 'sso_login_failed', 'sso_configured'
        )
    """)

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('event_type', sa.Enum(
            'login_success', 'login_failed', 'logout',
            'password_changed', 'password_reset_requested', 'password_reset_completed',
            'mfa_enabled', 'mfa_disabled', 'mfa_verified', 'mfa_failed',
            'user_registered', 'role_changed', 'user_deactivated', 'user_reactivated',
            'invitation_sent', 'invitation_accepted', 'invitation_expired', 'invitation_resent',
            'session_created', 'session_expired', 'session_revoked',
            'unauthorized_access', 'account_locked', 'account_unlocked', 'rate_limit_exceeded',
            'data_export_requested', 'data_export_completed', 'data_deletion_requested', 'data_deletion_completed',
            'sso_login_initiated', 'sso_login_success', 'sso_login_failed', 'sso_configured',
            name='auditeventtype'
        ), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create individual indexes
    op.create_index(op.f('ix_audit_logs_event_type'), 'audit_logs', ['event_type'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_organization_id'), 'audit_logs', ['organization_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'], unique=False)

    # Create composite indexes for common query patterns
    op.create_index('ix_audit_event_created', 'audit_logs', ['event_type', 'created_at'], unique=False)
    op.create_index('ix_audit_org_created', 'audit_logs', ['organization_id', 'created_at'], unique=False)
    op.create_index('ix_audit_user_created', 'audit_logs', ['user_id', 'created_at'], unique=False)


def downgrade() -> None:
    # Drop composite indexes
    op.drop_index('ix_audit_user_created', table_name='audit_logs')
    op.drop_index('ix_audit_org_created', table_name='audit_logs')
    op.drop_index('ix_audit_event_created', table_name='audit_logs')

    # Drop individual indexes
    op.drop_index(op.f('ix_audit_logs_created_at'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_organization_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_event_type'), table_name='audit_logs')

    # Drop table
    op.drop_table('audit_logs')

    # Drop enum type
    op.execute('DROP TYPE auditeventtype')
