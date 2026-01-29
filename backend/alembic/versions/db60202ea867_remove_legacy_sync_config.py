"""remove_legacy_sync_config

Revision ID: db60202ea867
Revises: da6777762256
Create Date: 2026-01-27 16:12:31.922037

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'db60202ea867'
down_revision: Union[str, None] = 'da6777762256'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Drop FK from source_materials -> sync_configs
    op.drop_constraint('source_materials_config_id_fkey', 'source_materials', type_='foreignkey')
    
    # 2. Drop config_id column
    op.drop_column('source_materials', 'config_id')
    
    # 3. Drop sync_configs table
    op.drop_table('sync_configs')
    
    # 4. Add source_id to source_materials
    op.add_column('source_materials', sa.Column('source_id', sa.UUID(), nullable=True))
    
    # 5. Add FK source_materials -> sources
    op.create_foreign_key(
        'fk_source_materials_sources', 
        'source_materials', 'sources', 
        ['source_id'], ['id'], 
        ondelete='SET NULL'
    )


def downgrade() -> None:
    # Reverse 5 & 4
    op.drop_constraint('fk_source_materials_sources', 'source_materials', type_='foreignkey')
    op.drop_column('source_materials', 'source_id')

    # Reverse 3: Recreate sync_configs
    op.create_table('sync_configs',
        sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
        sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=False),
        sa.Column('source_type', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
        sa.Column('external_id', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column('filter_config', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=False),
        sa.Column('last_synced_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column('status', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='sync_configs_user_id_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='sync_configs_pkey')
    )
    
    # Reverse 2: Add config_id back
    op.add_column('source_materials', sa.Column('config_id', sa.UUID(), autoincrement=False, nullable=True))
    
    # Reverse 1: Add FK back
    op.create_foreign_key(
        'source_materials_config_id_fkey',
        'source_materials', 'sync_configs',
        ['config_id'], ['id'],
        ondelete='SET NULL'
    )
