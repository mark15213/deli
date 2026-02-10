"""initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-02-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums first
    cardstatus_enum = postgresql.ENUM('pending', 'active', 'rejected', 'archived', name='cardstatus', create_type=False)
    cardstatus_enum.create(op.get_bind(), checkfirst=True)
    
    fsrsstate_enum = postgresql.ENUM('new', 'learning', 'review', 'relearning', name='fsrsstate', create_type=False)
    fsrsstate_enum.create(op.get_bind(), checkfirst=True)

    # 1. Users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(50), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('hashed_password', sa.String(255), nullable=True),
        sa.Column('settings', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # 2. OAuth Connections table
    op.create_table('oauth_connections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('provider_user_id', sa.String(255), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('provider', 'provider_user_id', name='uq_oauth_provider_uid'),
    )
    op.create_index('ix_oauth_connections_user_id', 'oauth_connections', ['user_id'])

    # 3. Sources table
    op.create_table('sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('parent_source_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sources.id', ondelete='CASCADE'), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('category', sa.String(20), nullable=False, server_default='SNAPSHOT'),
        sa.Column('connection_config', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('ingestion_rules', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('subscription_config', postgresql.JSONB(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='PENDING'),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_log', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_sources_user_id', 'sources', ['user_id'])
    op.create_index('ix_sources_parent_source_id', 'sources', ['parent_source_id'])

    # 4. Source Materials table
    op.create_table('source_materials',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sources.id', ondelete='SET NULL'), nullable=True),
        sa.Column('external_id', sa.String(255), nullable=False),
        sa.Column('external_url', sa.Text(), nullable=True),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('content_hash', sa.String(64), nullable=True),
        sa.Column('raw_snippet', sa.Text(), nullable=True),
        sa.Column('rich_data', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('user_id', 'external_id', name='uq_source_user_extid'),
    )
    op.create_index('ix_source_materials_user_id', 'source_materials', ['user_id'])

    # 5. Source Logs table
    op.create_table('source_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sources.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('lens_key', sa.String(100), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('extra_data', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_source_logs_source_id', 'source_logs', ['source_id'])

    # 6. Decks table
    op.create_table('decks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('cover_image_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_decks_owner_id', 'decks', ['owner_id'])

    # 7. Cards table
    op.create_table('cards',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_material_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('source_materials.id', ondelete='SET NULL'), nullable=True),
        sa.Column('type', sa.String(30), nullable=False),
        sa.Column('content', postgresql.JSONB(), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'active', 'rejected', 'archived', name='cardstatus', create_type=False), nullable=False, server_default='pending'),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('batch_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('batch_index', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_cards_owner_id', 'cards', ['owner_id'])
    op.create_index('ix_cards_batch_id', 'cards', ['batch_id'])

    # 8. Card-Decks association table
    op.create_table('card_decks',
        sa.Column('card_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cards.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('deck_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('decks.id', ondelete='CASCADE'), primary_key=True),
    )

    # 9. Deck Subscriptions table
    op.create_table('deck_subscriptions',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('deck_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('decks.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # 10. Study Progress table
    op.create_table('study_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('card_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cards.id', ondelete='CASCADE'), nullable=False),
        sa.Column('stability', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('difficulty', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('elapsed_days', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('scheduled_days', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('retrievability', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('state', postgresql.ENUM('new', 'learning', 'review', 'relearning', name='fsrsstate', create_type=False), nullable=False, server_default='new'),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_review_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('user_id', 'card_id', name='uq_study_user_card'),
    )
    op.create_index('idx_study_queue', 'study_progress', ['user_id', 'due_date'])

    # 11. Review Logs table
    op.create_table('review_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('card_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cards.id', ondelete='CASCADE'), nullable=False),
        sa.Column('grade', sa.Integer(), nullable=False),
        sa.Column('state_before', postgresql.ENUM('new', 'learning', 'review', 'relearning', name='fsrsstate', create_type=False), nullable=True),
        sa.Column('stability_before', sa.Float(), nullable=True),
        sa.Column('difficulty_before', sa.Float(), nullable=True),
        sa.Column('review_duration_ms', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_review_logs_user_id', 'review_logs', ['user_id'])
    op.create_index('ix_review_logs_card_id', 'review_logs', ['card_id'])


def downgrade() -> None:
    op.drop_table('review_logs')
    op.drop_table('study_progress')
    op.drop_table('deck_subscriptions')
    op.drop_table('card_decks')
    op.drop_table('cards')
    op.drop_table('decks')
    op.drop_table('source_logs')
    op.drop_table('source_materials')
    op.drop_table('sources')
    op.drop_table('oauth_connections')
    op.drop_table('users')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS cardstatus')
    op.execute('DROP TYPE IF EXISTS fsrsstate')
