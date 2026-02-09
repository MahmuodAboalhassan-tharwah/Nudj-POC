"""Create Framework Domain Config Table

Revision ID: 148f6bf7f33e
Revises: 3d4b5a8c9e7f1a2b
Create Date: 2026-02-09 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '148f6bf7f33e'
down_revision: Union[str, None] = '3d4b5a8c9e7f1a2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create framework_domain_configs table
    op.create_table('framework_domain_configs',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('domain_id', sa.Integer(), nullable=False),
        sa.Column('name_en', sa.String(), nullable=False),
        sa.Column('name_ar', sa.String(), nullable=False),
        sa.Column('description_en', sa.Text(), nullable=True),
        sa.Column('description_ar', sa.Text(), nullable=True),
        sa.Column('default_weight', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('domain_id')
    )

    # Create index on domain_id for faster lookups
    op.create_index('ix_framework_domain_configs_domain_id', 'framework_domain_configs', ['domain_id'])


def downgrade() -> None:
    # Drop index first
    op.drop_index('ix_framework_domain_configs_domain_id', table_name='framework_domain_configs')
    # Drop table
    op.drop_table('framework_domain_configs')
