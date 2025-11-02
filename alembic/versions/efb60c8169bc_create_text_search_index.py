"""create text search index

Revision ID: efb60c8169bc
Revises: ae5cd877a0b2
Create Date: 2025-11-01 18:47:15.518047

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'efb60c8169bc'
down_revision: Union[str, Sequence[str], None] = 'ae5cd877a0b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')
    op.execute('CREATE INDEX organizations_trgm_idx ON organizations USING GIN (name gin_trgm_ops)')


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('DROP INDEX organizations_trgm_idx ON organizations')
    op.execute('DROP EXTENSION pg_trgm')
