"""Add state_before and state_after to review_logs

Revision ID: 002dd43dbeb6
Revises: 67ba358d28e3
Create Date: 2026-03-04 14:30:37.658872

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002dd43dbeb6'
down_revision: Union[str, None] = '67ba358d28e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    result = bind.execute(sa.text(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name = 'review_logs' AND column_name = 'state_after'"
    ))
    if result.fetchone() is None:
        op.add_column('review_logs', sa.Column(
            'state_after',
            postgresql.ENUM('new', 'learning', 'review', 'relearning', name='fsrsstate', create_type=False),
            nullable=True
        ))


def downgrade() -> None:
    op.drop_column('review_logs', 'state_after')
