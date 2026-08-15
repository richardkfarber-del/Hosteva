"""add_status_and_rejection_notes

Revision ID: 78e19fe6a177
Revises: e05687434522
Create Date: 2026-06-04 19:40:25.461596

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '78e19fe6a177'
down_revision: Union[str, Sequence[str], None] = 'e05687434522'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('property_compliance', sa.Column('status', sa.String(length=50), nullable=True))
    op.add_column('property_compliance', sa.Column('rejection_notes', sa.String(length=500), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('property_compliance', 'rejection_notes')
    op.drop_column('property_compliance', 'status')
