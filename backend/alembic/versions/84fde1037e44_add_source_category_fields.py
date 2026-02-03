"""add_source_category_fields

Revision ID: 84fde1037e44
Revises: 71164794d318
Create Date: 2026-02-02 18:03:12.557822

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '84fde1037e44'
down_revision: Union[str, None] = '71164794d318'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()
    
    # 1. Create sources table if it doesn't exist
    if 'sources' not in existing_tables:
        op.create_table('sources',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('user_id', sa.UUID(), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('type', sa.String(length=50), nullable=False),
            sa.Column('category', sa.String(length=20), server_default='SNAPSHOT', nullable=False),
            sa.Column('connection_config', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
            sa.Column('ingestion_rules', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
            sa.Column('subscription_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('status', sa.String(length=20), server_default='PENDING', nullable=False),
            sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('next_sync_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('error_log', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_sources_user_id'), 'sources', ['user_id'], unique=False)
    else:
        # Add new columns to existing sources table
        columns = [col['name'] for col in inspector.get_columns('sources')]
        
        if 'category' not in columns:
            op.add_column('sources', sa.Column('category', sa.String(length=20), server_default='SNAPSHOT', nullable=False))
        
        if 'subscription_config' not in columns:
            op.add_column('sources', sa.Column('subscription_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
        
        if 'next_sync_at' not in columns:
            op.add_column('sources', sa.Column('next_sync_at', sa.DateTime(timezone=True), nullable=True))
    
    # 2. Create source_logs table if it doesn't exist
    if 'source_logs' not in existing_tables:
        op.create_table('source_logs',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('source_id', sa.UUID(), nullable=False),
            sa.Column('event_type', sa.String(length=50), nullable=False),
            sa.Column('lens_key', sa.String(length=100), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=False),
            sa.Column('message', sa.Text(), nullable=True),
            sa.Column('duration_ms', sa.Integer(), nullable=True),
            sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_source_logs_source_id'), 'source_logs', ['source_id'], unique=False)
    
    # 3. Create source_materials table if it doesn't exist
    if 'source_materials' not in existing_tables:
        op.create_table('source_materials',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('user_id', sa.UUID(), nullable=False),
            sa.Column('source_id', sa.UUID(), nullable=True),
            sa.Column('external_id', sa.String(length=255), nullable=False),
            sa.Column('external_url', sa.Text(), nullable=True),
            sa.Column('title', sa.Text(), nullable=True),
            sa.Column('content_hash', sa.String(length=64), nullable=True),
            sa.Column('raw_snippet', sa.Text(), nullable=True),
            sa.Column('rich_data', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id', 'external_id', name='uq_source_user_extid')
        )
        op.create_index(op.f('ix_source_materials_user_id'), 'source_materials', ['user_id'], unique=False)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()
    
    # Drop source_materials
    if 'source_materials' in existing_tables:
        op.drop_index(op.f('ix_source_materials_user_id'), table_name='source_materials')
        op.drop_table('source_materials')
    
    # Drop source_logs
    if 'source_logs' in existing_tables:
        op.drop_index(op.f('ix_source_logs_source_id'), table_name='source_logs')
        op.drop_table('source_logs')
    
    # Remove new columns from sources (but don't drop the table)
    if 'sources' in existing_tables:
        columns = [col['name'] for col in inspector.get_columns('sources')]
        
        if 'next_sync_at' in columns:
            op.drop_column('sources', 'next_sync_at')
        
        if 'subscription_config' in columns:
            op.drop_column('sources', 'subscription_config')
        
        if 'category' in columns:
            op.drop_column('sources', 'category')
