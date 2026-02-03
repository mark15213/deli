"""add_parent_source_id

Revision ID: f68b5eb22de6
Revises: 84fde1037e44
Create Date: 2026-02-03 18:53:04.287081

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f68b5eb22de6'
down_revision: Union[str, None] = '84fde1037e44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add parent_source_id column to sources table
    op.add_column('sources', sa.Column('parent_source_id', sa.UUID(), nullable=True))
    op.create_index(op.f('ix_sources_parent_source_id'), 'sources', ['parent_source_id'], unique=False)
    op.create_foreign_key('fk_sources_parent', 'sources', 'sources', ['parent_source_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    op.drop_constraint('fk_sources_parent', 'sources', type_='foreignkey')
    op.drop_index(op.f('ix_sources_parent_source_id'), table_name='sources')
    op.drop_column('sources', 'parent_source_id')
