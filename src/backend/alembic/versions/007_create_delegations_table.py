"""Create Assessment Delegations Table

Revision ID: 3d4b5a8c9e7f1a2b
Revises: 1f0edd12b1159e8b
Create Date: 2026-02-09 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3d4b5a8c9e7f1a2b'
down_revision: Union[str, None] = '1f0edd12b1159e8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create assessment_delegations table
    op.create_table(
        'assessment_delegations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('domain_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'REVOKED', name='delegation_status'), nullable=False),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['domain_id'], ['assessment_domains.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for optimized querying
    op.create_index(op.f('ix_assessment_delegations_assessment_id'), 'assessment_delegations', ['assessment_id'], unique=False)
    op.create_index(op.f('ix_assessment_delegations_domain_id'), 'assessment_delegations', ['domain_id'], unique=False)
    op.create_index(op.f('ix_assessment_delegations_user_id'), 'assessment_delegations', ['user_id'], unique=False)
    op.create_index(op.f('ix_assessment_delegations_status'), 'assessment_delegations', ['status'], unique=False)


def downgrade() -> None:
    # Drop indexes first
    op.drop_index(op.f('ix_assessment_delegations_status'), table_name='assessment_delegations')
    op.drop_index(op.f('ix_assessment_delegations_user_id'), table_name='assessment_delegations')
    op.drop_index(op.f('ix_assessment_delegations_domain_id'), table_name='assessment_delegations')
    op.drop_index(op.f('ix_assessment_delegations_assessment_id'), table_name='assessment_delegations')

    # Drop the table
    op.drop_table('assessment_delegations')
