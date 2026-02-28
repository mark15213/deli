"""add editor tables (source_edits, source_annotations, share_links)

Revision ID: add_editor_tables
Revises: clear_all_content
Create Date: 2026-02-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_editor_tables'
down_revision: Union[str, None] = 'clear_all_content'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- source_edits ---
    op.create_table('source_edits',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('source_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('content', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('plain_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_id', 'user_id', name='uq_source_edit_source_user')
    )
    op.create_index(op.f('ix_source_edits_source_id'), 'source_edits', ['source_id'], unique=False)
    op.create_index(op.f('ix_source_edits_user_id'), 'source_edits', ['user_id'], unique=False)

    # --- source_annotations ---
    op.create_table('source_annotations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('source_edit_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('type', sa.String(length=30), nullable=False),
        sa.Column('color', sa.String(length=20), nullable=True),
        sa.Column('anchor', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('body', sa.Text(), nullable=True),
        sa.Column('resolved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['source_edit_id'], ['source_edits.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_source_annotations_source_edit_id'), 'source_annotations', ['source_edit_id'], unique=False)
    op.create_index(op.f('ix_source_annotations_user_id'), 'source_annotations', ['user_id'], unique=False)

    # --- share_links ---
    op.create_table('share_links',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('source_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('token', sa.String(length=32), nullable=False),
        sa.Column('include_annotations', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token', name='uq_share_links_token')
    )
    op.create_index(op.f('ix_share_links_source_id'), 'share_links', ['source_id'], unique=False)
    op.create_index(op.f('ix_share_links_user_id'), 'share_links', ['user_id'], unique=False)
    op.create_index(op.f('ix_share_links_token'), 'share_links', ['token'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_share_links_token'), table_name='share_links')
    op.drop_index(op.f('ix_share_links_user_id'), table_name='share_links')
    op.drop_index(op.f('ix_share_links_source_id'), table_name='share_links')
    op.drop_table('share_links')

    op.drop_index(op.f('ix_source_annotations_user_id'), table_name='source_annotations')
    op.drop_index(op.f('ix_source_annotations_source_edit_id'), table_name='source_annotations')
    op.drop_table('source_annotations')

    op.drop_index(op.f('ix_source_edits_user_id'), table_name='source_edits')
    op.drop_index(op.f('ix_source_edits_source_id'), table_name='source_edits')
    op.drop_table('source_edits')
