"""activity depth constraint

Revision ID: b050606c1614
Revises: efb60c8169bc
Create Date: 2025-11-02 23:56:04.848055

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b050606c1614'
down_revision: Union[str, Sequence[str], None] = 'efb60c8169bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE OR REPLACE FUNCTION check_activity_depth()
        RETURNS TRIGGER AS $$
        DECLARE
            current_depth INTEGER;
        BEGIN
            IF NEW.parent_id IS NULL THEN
                RETURN NEW;
            END IF;

            WITH RECURSIVE hierarchy_path AS (
                SELECT
                    id,
                    parent_id,
                    1 AS depth
                FROM
                    activities
                WHERE
                    id = NEW.parent_id

                UNION ALL

                SELECT
                    a.id,
                    a.parent_id,
                    h.depth + 1
                FROM
                    activities a
                JOIN
                    hierarchy_path h ON a.id = h.parent_id
            )

            SELECT MAX(depth) INTO current_depth
            FROM hierarchy_path;

            IF NOT FOUND OR current_depth IS NULL THEN
                RETURN NEW;
            END IF;

            IF current_depth >= 3 THEN
                RAISE EXCEPTION 'Maximum hierarchy depth of 3 exceeded. Parent activity (id=%) is already at depth %.', NEW.parent_id, current_depth;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER enforce_max_depth_trigger
            BEFORE INSERT OR UPDATE ON activities
            FOR EACH ROW
            EXECUTE FUNCTION check_activity_depth();
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('DROP TRIGGER IF EXISTS enforce_max_depth_trigger ON activities;')
    op.execute('DROP FUNCTION IF EXISTS check_activity_depth();')
