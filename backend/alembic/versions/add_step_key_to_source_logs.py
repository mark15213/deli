"""add step_key to source_logs

Revision ID: add_step_key_to_source_logs
Revises: cd9893bf19fd
Create Date: 2026-02-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_step_key_to_source_logs'
down_revision: Union[str, None] = '002_add_pipeline_templates'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('source_logs', sa.Column('step_key', sa.String(100), nullable=True))


def downgrade() -> None:
    op.drop_column('source_logs', 'step_key')
