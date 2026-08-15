"""add_validation_constraints

Revision ID: d207191b3943
Revises: 
Create Date: 2026-06-04 07:04:47.498308

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd207191b3943'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('municipal_codes', sa.Column('stay_restriction_days', sa.Integer(), nullable=True))
    op.add_column('municipal_codes', sa.Column('max_rentals_per_year', sa.Integer(), nullable=True))
    op.add_column('municipal_codes', sa.Column('requires_permit', sa.Boolean(), nullable=True))
    op.add_column('municipal_codes', sa.Column('permit_name', sa.String(length=100), nullable=True))
    op.add_column('municipal_codes', sa.Column('source_url', sa.String(length=255), nullable=True))
    op.add_column('municipal_codes', sa.Column('tax_rate', sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('municipal_codes', 'tax_rate')
    op.drop_column('municipal_codes', 'source_url')
    op.drop_column('municipal_codes', 'permit_name')
    op.drop_column('municipal_codes', 'requires_permit')
    op.drop_column('municipal_codes', 'max_rentals_per_year')
    op.drop_column('municipal_codes', 'stay_restriction_days')
