"""add card bookmarks table

Revision ID: cd9893bf19fd
Revises: 001_initial_schema
Create Date: 2026-02-12 19:01:07.205941

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'cd9893bf19fd'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('card_bookmarks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('card_id', sa.UUID(), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['card_id'], ['cards.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'card_id', name='uq_bookmark_user_card')
    )
    op.create_index(op.f('ix_card_bookmarks_card_id'), 'card_bookmarks', ['card_id'], unique=False)
    op.create_index(op.f('ix_card_bookmarks_user_id'), 'card_bookmarks', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_card_bookmarks_user_id'), table_name='card_bookmarks')
    op.drop_index(op.f('ix_card_bookmarks_card_id'), table_name='card_bookmarks')
    op.drop_table('card_bookmarks')
