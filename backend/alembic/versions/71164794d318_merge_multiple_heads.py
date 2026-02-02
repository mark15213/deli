"""merge_multiple_heads

Revision ID: 71164794d318
Revises: 1eacd8565ebb, 32c51f0bfb26
Create Date: 2026-02-02 18:02:48.357395

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71164794d318'
down_revision: Union[str, None] = ('1eacd8565ebb', '32c51f0bfb26')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
