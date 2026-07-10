"""enable_vector_extension

Revision ID: ecbe016392bf
Revises: 
Create Date: 2026-07-10 23:10:32.250053

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ecbe016392bf'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Menghidupkan kapabilitas Vector Database di Supabase                                                      
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    pass


def downgrade() -> None:
    # Mematikan ekstensi saat rollback ke versi nol                                                             
    op.execute("DROP EXTENSION IF EXISTS vector")  
    pass
