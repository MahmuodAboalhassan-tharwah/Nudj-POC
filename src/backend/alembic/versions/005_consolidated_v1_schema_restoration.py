"""consolidated v1 schema restoration

Revision ID: 005
Revises: 004
Create Date: 2024-10-24 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None

def upgrade():
    # Enums
    op.execute("CREATE TYPE role AS ENUM ('super_admin', 'analyst', 'client_admin', 'assessor')")
    op.execute("CREATE TYPE ssoprovider AS ENUM ('azure_ad', 'google')")
    op.execute("CREATE TYPE deletionstatus AS ENUM ('pending', 'processing', 'completed', 'rejected')")
    op.execute("CREATE TYPE delegation_status AS ENUM ('ACTIVE', 'REVOKED')")
    op.execute("CREATE TYPE auditeventtype AS ENUM ("
               "'login_success', 'login_failed', 'logout', "
               "'password_changed', 'password_reset_requested', 'password_reset_completed', "
               "'mfa_enabled', 'mfa_disabled', 'mfa_verified', 'mfa_failed', "
               "'user_registered', 'role_changed', 'user_deactivated', 'user_reactivated', "
               "'invitation_sent', 'invitation_accepted', 'invitation_expired', 'invitation_resent', "
               "'session_created', 'session_expired', 'session_revoked', "
               "'unauthorized_access', 'account_locked', 'account_unlocked', 'rate_limit_exceeded', "
               "'data_export_requested', 'data_export_completed', 'data_deletion_requested', 'data_deletion_completed', "
               "'sso_login_initiated', 'sso_login_success', 'sso_login_failed', 'sso_configured')")
    op.execute("CREATE TYPE notificationtype AS ENUM ('info', 'success', 'warning', 'error', 'action_required')")

    # 1. Invitations (needs to exist for User link)
    op.create_table(
        'invitations',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('token', sa.String(length=128), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('super_admin', 'analyst', 'client_admin', 'assessor', name='role'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('domain_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('invited_by', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )
    op.create_index(op.f('ix_invitations_email'), 'invitations', ['email'], unique=False)

    # 2. Users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('name_ar', sa.String(length=255), nullable=False),
        sa.Column('name_en', sa.String(length=255), nullable=False),
        sa.Column('phone_sa', sa.String(length=20), nullable=True),
        sa.Column('role', sa.Enum('super_admin', 'analyst', 'client_admin', 'assessor', name='role'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('mfa_enabled', sa.Boolean(), nullable=False),
        sa.Column('mfa_secret', sa.String(length=255), nullable=True),
        sa.Column('sso_provider', sa.Enum('azure_ad', 'google', name='ssoprovider'), nullable=True),
        sa.Column('sso_external_id', sa.String(length=255), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by_invitation_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by_invitation_id'], ['invitations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index('ix_users_org_role', 'users', ['organization_id', 'role'], unique=False)
    op.create_index('ix_users_sso', 'users', ['sso_provider', 'sso_external_id'], unique=False)

    # Now fix invitations FK
    op.create_foreign_key('fk_invitations_invited_by', 'invitations', 'users', ['invited_by'], ['id'], ondelete='SET NULL')

    # 3. Refresh Tokens
    op.create_table(
        'refresh_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('device_info', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_refresh_tokens_token_hash'), 'refresh_tokens', ['token_hash'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_user_id'), 'refresh_tokens', ['user_id'], unique=False)

    # 4. Password Reset Tokens
    op.create_table(
        'password_reset_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_password_reset_tokens_token_hash'), 'password_reset_tokens', ['token_hash'], unique=False)
    op.create_index(op.f('ix_password_reset_tokens_user_id'), 'password_reset_tokens', ['user_id'], unique=False)

    # 5. User Sessions
    op.create_table(
        'user_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('session_token_hash', sa.String(length=64), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_sessions_session_token_hash'), 'user_sessions', ['session_token_hash'], unique=False)
    op.create_index(op.f('ix_user_sessions_user_id'), 'user_sessions', ['user_id'], unique=False)

    # 6. User Domain Assignments
    op.create_table(
        'user_domain_assignments',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('domain_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('assigned_by', postgresql.UUID(as_uuid=False), nullable=True),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'assessment_id', name='uq_user_assessment_domain')
    )
    op.create_index(op.f('ix_user_domain_assignments_assessment_id'), 'user_domain_assignments', ['assessment_id'], unique=False)
    op.create_index(op.f('ix_user_domain_assignments_user_id'), 'user_domain_assignments', ['user_id'], unique=False)

    # 7. Analyst Org Assignments
    op.create_table(
        'analyst_org_assignments',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('assigned_by', postgresql.UUID(as_uuid=False), nullable=True),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'organization_id', name='uq_analyst_org')
    )
    op.create_index(op.f('ix_analyst_org_assignments_organization_id'), 'analyst_org_assignments', ['organization_id'], unique=False)
    op.create_index(op.f('ix_analyst_org_assignments_user_id'), 'analyst_org_assignments', ['user_id'], unique=False)

    # 8. SSO Configurations
    op.create_table(
        'sso_configurations',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('provider', sa.Enum('azure_ad', 'google', name='ssoprovider'), nullable=False),
        sa.Column('tenant_id', sa.String(length=255), nullable=True),
        sa.Column('client_id', sa.String(length=255), nullable=False),
        sa.Column('client_secret_encrypted', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('configured_by', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['configured_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'provider', name='uq_org_sso_provider')
    )
    op.create_index(op.f('ix_sso_configurations_organization_id'), 'sso_configurations', ['organization_id'], unique=False)

    # 9. Data Deletion Requests
    op.create_table(
        'data_deletion_requests',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('requested_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'rejected', name='deletionstatus'), nullable=False),
        sa.Column('processed_by', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['processed_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_data_deletion_requests_user_id'), 'data_deletion_requests', ['user_id'], unique=False)

    # 10. Notifications
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('link', sa.String(length=500), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'], unique=False)

    # 11. Comments
    op.create_table(
        'comments',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('response_id', postgresql.UUID(), nullable=False),
        sa.Column('parent_id', postgresql.UUID(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['comments.id'], ),
        sa.ForeignKeyConstraint(['response_id'], ['assessment_element_responses.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comments_parent_id'), 'comments', ['parent_id'], unique=False)
    op.create_index(op.f('ix_comments_response_id'), 'comments', ['response_id'], unique=False)
    op.create_index(op.f('ix_comments_user_id'), 'comments', ['user_id'], unique=False)

    # 12. Framework Domain Configs
    op.create_table(
        'framework_domain_configs',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('domain_id', sa.Integer(), nullable=False),
        sa.Column('name_en', sa.String(), nullable=False),
        sa.Column('name_ar', sa.String(), nullable=False),
        sa.Column('description_en', sa.Text(), nullable=True),
        sa.Column('description_ar', sa.Text(), nullable=True),
        sa.Column('default_weight', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_framework_domain_configs_domain_id'), 'framework_domain_configs', ['domain_id'], unique=True)

    # 13. Assessment Delegations
    op.create_table(
        'assessment_delegations',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('assessment_id', postgresql.UUID(), nullable=False),
        sa.Column('domain_id', postgresql.UUID(), nullable=True),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('created_by', postgresql.UUID(), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'REVOKED', name='delegation_status'), nullable=False),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['domain_id'], ['assessment_domains.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assessment_delegations_assessment_id'), 'assessment_delegations', ['assessment_id'], unique=False)
    op.create_index(op.f('ix_assessment_delegations_domain_id'), 'assessment_delegations', ['domain_id'], unique=False)
    op.create_index(op.f('ix_assessment_delegations_status'), 'assessment_delegations', ['status'], unique=False)
    op.create_index(op.f('ix_assessment_delegations_user_id'), 'assessment_delegations', ['user_id'], unique=False)

    # 14. Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('event_type', sa.Enum('login_success', 'login_failed', 'logout', 'password_changed', 'password_reset_requested', 'password_reset_completed', 'mfa_enabled', 'mfa_disabled', 'mfa_verified', 'mfa_failed', 'user_registered', 'role_changed', 'user_deactivated', 'user_reactivated', 'invitation_sent', 'invitation_accepted', 'invitation_expired', 'invitation_resent', 'session_created', 'session_expired', 'session_revoked', 'unauthorized_access', 'account_locked', 'account_unlocked', 'rate_limit_exceeded', 'data_export_requested', 'data_export_completed', 'data_deletion_requested', 'data_deletion_completed', 'sso_login_initiated', 'sso_login_success', 'sso_login_failed', 'sso_configured', name='auditeventtype'), nullable=False),
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
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_audit_logs_event_type'), 'audit_logs', ['event_type'], unique=False)
    op.create_index(op.f('ix_audit_logs_organization_id'), 'audit_logs', ['organization_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index('ix_audit_event_created', 'audit_logs', ['event_type', 'created_at'], unique=False)
    op.create_index('ix_audit_org_created', 'audit_logs', ['organization_id', 'created_at'], unique=False)
    op.create_index('ix_audit_user_created', 'audit_logs', ['user_id', 'created_at'], unique=False)


def downgrade():
    op.drop_index('ix_audit_user_created', table_name='audit_logs')
    op.drop_index('ix_audit_org_created', table_name='audit_logs')
    op.drop_index('ix_audit_event_created', table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_organization_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_event_type'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_created_at'), table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_index(op.f('ix_assessment_delegations_user_id'), table_name='assessment_delegations')
    op.drop_index(op.f('ix_assessment_delegations_status'), table_name='assessment_delegations')
    op.drop_index(op.f('ix_assessment_delegations_domain_id'), table_name='assessment_delegations')
    op.drop_index(op.f('ix_assessment_delegations_assessment_id'), table_name='assessment_delegations')
    op.drop_table('assessment_delegations')
    op.drop_index(op.f('ix_framework_domain_configs_domain_id'), table_name='framework_domain_configs')
    op.drop_table('framework_domain_configs')
    op.drop_index(op.f('ix_comments_user_id'), table_name='comments')
    op.drop_index(op.f('ix_comments_response_id'), table_name='comments')
    op.drop_index(op.f('ix_comments_parent_id'), table_name='comments')
    op.drop_table('comments')
    op.drop_index(op.f('ix_notifications_user_id'), table_name='notifications')
    op.drop_table('notifications')
    op.drop_index(op.f('ix_data_deletion_requests_user_id'), table_name='data_deletion_requests')
    op.drop_table('data_deletion_requests')
    op.drop_index(op.f('ix_sso_configurations_organization_id'), table_name='sso_configurations')
    op.drop_table('sso_configurations')
    op.drop_index(op.f('ix_analyst_org_assignments_user_id'), table_name='analyst_org_assignments')
    op.drop_index(op.f('ix_analyst_org_assignments_organization_id'), table_name='analyst_org_assignments')
    op.drop_table('analyst_org_assignments')
    op.drop_index(op.f('ix_user_domain_assignments_user_id'), table_name='user_domain_assignments')
    op.drop_index(op.f('ix_user_domain_assignments_assessment_id'), table_name='user_domain_assignments')
    op.drop_table('user_domain_assignments')
    op.drop_index(op.f('ix_user_sessions_user_id'), table_name='user_sessions')
    op.drop_index(op.f('ix_user_sessions_session_token_hash'), table_name='user_sessions')
    op.drop_table('user_sessions')
    op.drop_index(op.f('ix_password_reset_tokens_user_id'), table_name='password_reset_tokens')
    op.drop_index(op.f('ix_password_reset_tokens_token_hash'), table_name='password_reset_tokens')
    op.drop_table('password_reset_tokens')
    op.drop_index(op.f('ix_refresh_tokens_user_id'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_token_hash'), table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index('ix_users_sso', table_name='users')
    op.drop_index('ix_users_org_role', table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_invitations_email'), table_name='invitations')
    op.drop_table('invitations')
    
    op.execute("DROP TYPE notificationtype")
    op.execute("DROP TYPE auditeventtype")
    op.execute("DROP TYPE delegation_status")
    op.execute("DROP TYPE deletionstatus")
    op.execute("DROP TYPE ssoprovider")
    op.execute("DROP TYPE role")
