"""Clear all content data from production

Revision ID: clear_all_content
Revises: dc9ebe2495ec
Create Date: 2026-02-26 17:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'clear_all_content'
down_revision: Union[str, None] = 'dc9ebe2495ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    """Check if a table exists."""
    bind = op.get_bind()
    result = bind.execute(sa.text(
        "SELECT 1 FROM information_schema.tables "
        "WHERE table_name = :table AND table_schema = 'public'"
    ), {"table": table_name})
    return result.fetchone() is not None


def upgrade() -> None:
    """TRUNCATE all content tables using CASCADE to handle FK dependencies."""
    # Use TRUNCATE ... CASCADE which handles FK ordering automatically in Postgres
    tables_to_clear = [
        'review_logs',
        'study_progress',
        'card_bookmarks',
        'source_logs',
        'card_decks',
        'deck_subscriptions',
        'cards',
        'source_materials',
        'decks',
        'sources',
    ]

    bind = op.get_bind()
    for table in tables_to_clear:
        if _table_exists(table):
            bind.execute(sa.text(f'TRUNCATE TABLE "{table}" CASCADE'))


def downgrade() -> None:
    # Data deletion is irreversible - no downgrade possible
    pass
