"""enable_vector_extension

Revision ID: 6af203b52974
Revises: ecbe016392bf
Create Date: 2026-07-10 23:26:42.489108

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6af203b52974'
down_revision: Union[str, Sequence[str], None] = 'ecbe016392bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP EXTENSION IF EXISTS vector")
