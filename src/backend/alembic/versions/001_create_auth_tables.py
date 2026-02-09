"""Create Auth Tables

Revision ID: 001_create_auth_tables
Revises:
Create Date: 2026-02-09 10:00:00.000000

Creates all authentication and authorization tables:
- users: Core user entity with role, MFA, SSO support
- invitations: Secure invitation tokens for registration
- refresh_tokens: JWT refresh token tracking
- password_reset_tokens: Password reset flow tokens
- user_sessions: Active session tracking
- user_domain_assignments: Assessor domain access
- analyst_org_assignments: Analyst organization access
- sso_configurations: Per-org SSO settings
- data_deletion_requests: PDPL compliance requests

Includes enums: Role, SSOProvider, DeletionStatus
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_create_auth_tables'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create Enums
    role_enum = sa.Enum('SUPER_ADMIN', 'ANALYST', 'CLIENT_ADMIN', 'ASSESSOR', name='role')
    sso_provider_enum = sa.Enum('AZURE_AD', 'GOOGLE', name='ssoprovider')
    deletion_status_enum = sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'REJECTED', name='deletionstatus')

    role_enum.create(op.get_bind())
    sso_provider_enum.create(op.get_bind())
    deletion_status_enum.create(op.get_bind())

    # Create invitations table (no dependencies, needed for users.created_by_invitation_id FK)
    op.create_table('invitations',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('token', sa.String(length=128), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('role', role_enum, nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('domain_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('invited_by', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invitations_token'), 'invitations', ['token'], unique=True)
    op.create_index(op.f('ix_invitations_email'), 'invitations', ['email'], unique=False)

    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('name_ar', sa.String(length=255), nullable=False),
        sa.Column('name_en', sa.String(length=255), nullable=False),
        sa.Column('phone_sa', sa.String(length=20), nullable=True),
        sa.Column('role', role_enum, nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('mfa_enabled', sa.Boolean(), nullable=False, default=False),
        sa.Column('mfa_secret', sa.String(length=255), nullable=True),
        sa.Column('sso_provider', sso_provider_enum, nullable=True),
        sa.Column('sso_external_id', sa.String(length=255), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by_invitation_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by_invitation_id'], ['invitations.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)
    op.create_index(op.f('ix_users_organization_id'), 'users', ['organization_id'], unique=False)
    op.create_index('ix_users_org_role', 'users', ['organization_id', 'role'], unique=False)
    op.create_index('ix_users_sso', 'users', ['sso_provider', 'sso_external_id'], unique=False)

    # Add invited_by FK to invitations (now that users table exists)
    op.create_foreign_key(
        'fk_invitations_invited_by', 'invitations', 'users',
        ['invited_by'], ['id'], ondelete='SET NULL'
    )

    # Create refresh_tokens table
    op.create_table('refresh_tokens',
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
    op.create_index(op.f('ix_refresh_tokens_user_id'), 'refresh_tokens', ['user_id'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_token_hash'), 'refresh_tokens', ['token_hash'], unique=False)

    # Create password_reset_tokens table
    op.create_table('password_reset_tokens',
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
    op.create_index(op.f('ix_password_reset_tokens_user_id'), 'password_reset_tokens', ['user_id'], unique=False)
    op.create_index(op.f('ix_password_reset_tokens_token_hash'), 'password_reset_tokens', ['token_hash'], unique=False)

    # Create user_sessions table
    op.create_table('user_sessions',
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
    op.create_index(op.f('ix_user_sessions_user_id'), 'user_sessions', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_sessions_session_token_hash'), 'user_sessions', ['session_token_hash'], unique=False)

    # Create user_domain_assignments table
    # Note: assessment_id FK will be created when assessments table is created in migration 003
    op.create_table('user_domain_assignments',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('domain_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('assigned_by', postgresql.UUID(as_uuid=False), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'assessment_id', name='uq_user_assessment_domain')
    )
    op.create_index(op.f('ix_user_domain_assignments_user_id'), 'user_domain_assignments', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_domain_assignments_assessment_id'), 'user_domain_assignments', ['assessment_id'], unique=False)

    # Create analyst_org_assignments table
    # Note: organization_id FK will be created when organizations table is created in migration 004
    op.create_table('analyst_org_assignments',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('assigned_by', postgresql.UUID(as_uuid=False), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'organization_id', name='uq_analyst_org')
    )
    op.create_index(op.f('ix_analyst_org_assignments_user_id'), 'analyst_org_assignments', ['user_id'], unique=False)
    op.create_index(op.f('ix_analyst_org_assignments_organization_id'), 'analyst_org_assignments', ['organization_id'], unique=False)

    # Create sso_configurations table
    # Note: organization_id FK will be created when organizations table is created in migration 004
    op.create_table('sso_configurations',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('provider', sso_provider_enum, nullable=False),
        sa.Column('tenant_id', sa.String(length=255), nullable=True),
        sa.Column('client_id', sa.String(length=255), nullable=False),
        sa.Column('client_secret_encrypted', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('configured_by', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['configured_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'provider', name='uq_org_sso_provider')
    )
    op.create_index(op.f('ix_sso_configurations_organization_id'), 'sso_configurations', ['organization_id'], unique=False)

    # Create data_deletion_requests table
    op.create_table('data_deletion_requests',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('requested_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', deletion_status_enum, nullable=False, default='PENDING'),
        sa.Column('processed_by', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['processed_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_data_deletion_requests_user_id'), 'data_deletion_requests', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_data_deletion_requests_user_id'), table_name='data_deletion_requests')
    op.drop_table('data_deletion_requests')

    op.drop_index(op.f('ix_sso_configurations_organization_id'), table_name='sso_configurations')
    op.drop_table('sso_configurations')

    op.drop_index(op.f('ix_analyst_org_assignments_organization_id'), table_name='analyst_org_assignments')
    op.drop_index(op.f('ix_analyst_org_assignments_user_id'), table_name='analyst_org_assignments')
    op.drop_table('analyst_org_assignments')

    op.drop_index(op.f('ix_user_domain_assignments_assessment_id'), table_name='user_domain_assignments')
    op.drop_index(op.f('ix_user_domain_assignments_user_id'), table_name='user_domain_assignments')
    op.drop_table('user_domain_assignments')

    op.drop_index(op.f('ix_user_sessions_session_token_hash'), table_name='user_sessions')
    op.drop_index(op.f('ix_user_sessions_user_id'), table_name='user_sessions')
    op.drop_table('user_sessions')

    op.drop_index(op.f('ix_password_reset_tokens_token_hash'), table_name='password_reset_tokens')
    op.drop_index(op.f('ix_password_reset_tokens_user_id'), table_name='password_reset_tokens')
    op.drop_table('password_reset_tokens')

    op.drop_index(op.f('ix_refresh_tokens_token_hash'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_user_id'), table_name='refresh_tokens')
    op.drop_table('refresh_tokens')

    # Drop FK from invitations before dropping users
    op.drop_constraint('fk_invitations_invited_by', 'invitations', type_='foreignkey')

    op.drop_index('ix_users_sso', table_name='users')
    op.drop_index('ix_users_org_role', table_name='users')
    op.drop_index(op.f('ix_users_organization_id'), table_name='users')
    op.drop_index(op.f('ix_users_role'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

    op.drop_index(op.f('ix_invitations_email'), table_name='invitations')
    op.drop_index(op.f('ix_invitations_token'), table_name='invitations')
    op.drop_table('invitations')

    # Drop Enums
    op.execute("DROP TYPE deletionstatus")
    op.execute("DROP TYPE ssoprovider")
    op.execute("DROP TYPE role")
