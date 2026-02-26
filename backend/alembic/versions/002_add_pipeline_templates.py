"""add pipeline_templates table

Revision ID: 002_add_pipeline_templates
Revises: cd9893bf19fd
Create Date: 2026-02-18 08:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_add_pipeline_templates'
down_revision: Union[str, None] = 'cd9893bf19fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('pipeline_templates',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), server_default='', nullable=False),
        sa.Column('is_system', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('definition', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_pipeline_templates_user_id'), 'pipeline_templates', ['user_id'], unique=False)
    op.create_index(op.f('ix_pipeline_templates_is_system'), 'pipeline_templates', ['is_system'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_pipeline_templates_is_system'), table_name='pipeline_templates')
    op.drop_index(op.f('ix_pipeline_templates_user_id'), table_name='pipeline_templates')
    op.drop_table('pipeline_templates')
