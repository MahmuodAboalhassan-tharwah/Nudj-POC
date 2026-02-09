"""Create Organization Table

Revision ID: 004_create_organization_table
Revises: 003_create_assessment_tables
Create Date: 2026-02-08 21:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004_create_organization_table'
down_revision: Union[str, None] = '003_create_assessment_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create organizations table
    op.create_table('organizations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name_ar', sa.String(length=255), nullable=False),
        sa.Column('name_en', sa.String(length=255), nullable=False),
        sa.Column('cr_number', sa.String(length=50), nullable=True),
        sa.Column('sector', sa.String(length=100), nullable=True),
        sa.Column('size', sa.String(length=50), nullable=True),
        sa.Column('region', sa.String(length=100), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add Foreign Keys
    # We use batch_alter_table for SQLite compatibility if needed, though strictly Postgres supports direct add_constraint
    # For now, standard op.create_foreign_key
    
    # Check if 'users' table exists and add FK
    # Note: validation of existence is tricky in offline mode, so we assume it exists as per 001/003 logic
    op.create_foreign_key(
        'fk_users_organization_id', 'users', 'organizations',
        ['organization_id'], ['id'], ondelete='SET NULL'
    )
    
    # Add FK to assessments
    op.create_foreign_key(
        'fk_assessments_organization_id', 'assessments', 'organizations',
        ['organization_id'], ['id']
    )


def downgrade() -> None:
    op.drop_constraint('fk_assessments_organization_id', 'assessments', type_='foreignkey')
    op.drop_constraint('fk_users_organization_id', 'users', type_='foreignkey')
    op.drop_table('organizations')
