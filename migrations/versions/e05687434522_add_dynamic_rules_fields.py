"""add_dynamic_rules_fields

Revision ID: e05687434522
Revises: d207191b3943
Create Date: 2026-06-04 07:54:02.077094

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e05687434522'
down_revision: Union[str, Sequence[str], None] = 'd207191b3943'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('municipal_codes', sa.Column('is_allowed', sa.Boolean(), nullable=True))
    op.add_column('municipal_codes', sa.Column('zoning_code', sa.String(length=50), nullable=True))
    op.add_column('municipal_codes', sa.Column('property_type', sa.String(length=50), nullable=True))
    op.add_column('municipal_codes', sa.Column('rejection_reason', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('municipal_codes', 'rejection_reason')
    op.drop_column('municipal_codes', 'property_type')
    op.drop_column('municipal_codes', 'zoning_code')
    op.drop_column('municipal_codes', 'is_allowed')
