"""add rating to review logs

Revision ID: 67ba358d28e3
Revises: add_editor_tables
Create Date: 2026-03-03 19:54:01.137959

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '67ba358d28e3'
down_revision: Union[str, None] = 'add_editor_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('review_logs')]
    
    if 'rating' not in columns:
        # Add rating column with a default of 1 (Again) so it doesn't break existing rows
        op.add_column('review_logs', sa.Column('rating', sa.Integer(), server_default='1', nullable=False))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('review_logs')]
    
    if 'rating' in columns:
        op.drop_column('review_logs', 'rating')
