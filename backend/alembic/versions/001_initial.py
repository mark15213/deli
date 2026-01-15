"""Initial database schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('preferences', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Create notion_connections table
    op.create_table(
        'notion_connections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('access_token_encrypted', sa.Text, nullable=False),
        sa.Column('workspace_id', sa.String(255), nullable=True),
        sa.Column('workspace_name', sa.String(255), nullable=True),
        sa.Column('selected_databases', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('last_synced_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Create quiz_status enum
    quiz_status = postgresql.ENUM('pending', 'approved', 'rejected', name='quiz_status', create_type=False)
    quiz_status.create(op.get_bind(), checkfirst=True)

    # Create quiz_type enum
    quiz_type = postgresql.ENUM(
        'mcq', 'true_false', 'cloze', 'code_output', 'spot_bug', 'reorder', 'flashcard',
        name='quiz_type', create_type=False
    )
    quiz_type.create(op.get_bind(), checkfirst=True)

    # Create quizzes table
    op.create_table(
        'quizzes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('type', postgresql.ENUM('mcq', 'true_false', 'cloze', 'code_output', 'spot_bug', 'reorder', 'flashcard', name='quiz_type', create_type=False), nullable=False),
        sa.Column('question', sa.Text, nullable=False),
        sa.Column('options', postgresql.JSONB, nullable=True),
        sa.Column('answer', sa.Text, nullable=False),
        sa.Column('explanation', sa.Text, nullable=True),
        sa.Column('source_page_id', sa.String(255), nullable=True),
        sa.Column('source_block_id', sa.String(255), nullable=True),
        sa.Column('source_page_title', sa.String(500), nullable=True),
        sa.Column('source_deep_link', sa.Text, nullable=True),
        sa.Column('tags', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('difficulty', sa.String(50), nullable=True),
        sa.Column('status', postgresql.ENUM('pending', 'approved', 'rejected', name='quiz_status', create_type=False), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Create review_records table
    op.create_table(
        'review_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('quiz_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('rating', sa.Integer, nullable=False),
        sa.Column('fsrs_state', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('reviewed_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('next_review_at', sa.DateTime, nullable=False, index=True),
    )


def downgrade() -> None:
    op.drop_table('review_records')
    op.drop_table('quizzes')
    op.drop_table('notion_connections')
    op.drop_table('users')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS quiz_status')
    op.execute('DROP TYPE IF EXISTS quiz_type')
