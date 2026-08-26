"""Update chk_ordinance_id_format

Revision ID: 5714603a9e35
Revises: d278a49c96b8
Create Date: 2026-04-18 06:22:43.087919

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5714603a9e35'
down_revision: Union[str, Sequence[str], None] = 'd278a49c96b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint('chk_ordinance_id_format', 'municipal_codes', type_='check')
    op.create_check_constraint(
        'chk_ordinance_id_format',
        'municipal_codes',
        "ordinance_id ~ '^[A-Z0-9]{3,10}-[A-Z0-9]{2,10}$'"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('chk_ordinance_id_format', 'municipal_codes', type_='check')
    op.create_check_constraint(
        'chk_ordinance_id_format',
        'municipal_codes',
        "ordinance_id ~ '^[A-Z0-9\-]+$'"
    )
