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
    op.create_index(
        op.f('organizations_trgm_idx'),
        'organizations',
        ['name'],
        unique=False,
        postgresql_ops={'name': 'gin_trgm_ops'},
        postgresql_using='gin',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f('organizations_trgm_idx'),
        table_name='organizations',
        postgresql_ops={'name': 'gin_trgm_ops'},
        postgresql_using='gin',
    )
    op.execute('DROP EXTENSION pg_trgm')
