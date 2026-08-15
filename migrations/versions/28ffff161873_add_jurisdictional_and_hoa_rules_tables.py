"""add_jurisdictional_and_hoa_rules_tables

Revision ID: 28ffff161873
Revises: 78e19fe6a177
Create Date: 2026-06-13 07:15:40.605927

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '28ffff161873'
down_revision: Union[str, Sequence[str], None] = '78e19fe6a177'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('hoa_rules',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('hoa_name', sa.String(length=150), nullable=False),
    sa.Column('location', sa.String(length=150), nullable=False),
    sa.Column('str_permitted', sa.String(length=100), nullable=False),
    sa.Column('minimum_lease_stay', sa.String(length=100), nullable=True),
    sa.Column('rules_available', sa.Boolean(), nullable=True),
    sa.Column('official_website', sa.String(length=250), nullable=True),
    sa.Column('last_confirmed_date', sa.Date(), nullable=True),
    sa.Column('key_rules_notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('hoa_name', 'location', name='uq_hoa_rules_name_location')
    )
    op.create_index(op.f('ix_hoa_rules_hoa_name'), 'hoa_rules', ['hoa_name'], unique=False)
    
    op.add_column('municipal_codes', sa.Column('jurisdiction_type', sa.String(length=50), nullable=True))
    op.add_column('municipal_codes', sa.Column('str_permitted_raw', sa.String(length=100), nullable=True))
    op.add_column('municipal_codes', sa.Column('permit_required_raw', sa.String(length=50), nullable=True))
    op.add_column('municipal_codes', sa.Column('minimum_stay_requirement', sa.String(length=255), nullable=True))
    op.add_column('municipal_codes', sa.Column('occupancy_limits', sa.String(length=255), nullable=True))
    op.add_column('municipal_codes', sa.Column('tax_rate_registration_fee', sa.String(length=255), nullable=True))
    op.add_column('municipal_codes', sa.Column('last_verified_date', sa.Date(), nullable=True))

    with op.batch_alter_table('municipal_codes') as batch_op:
        batch_op.create_unique_constraint('uq_municipal_codes_name_type', ['municipality_name', 'jurisdiction_type'])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('municipal_codes') as batch_op:
        batch_op.drop_constraint('uq_municipal_codes_name_type', type_='unique')
        
    op.drop_column('municipal_codes', 'last_verified_date')
    op.drop_column('municipal_codes', 'tax_rate_registration_fee')
    op.drop_column('municipal_codes', 'occupancy_limits')
    op.drop_column('municipal_codes', 'minimum_stay_requirement')
    op.drop_column('municipal_codes', 'permit_required_raw')
    op.drop_column('municipal_codes', 'str_permitted_raw')
    op.drop_column('municipal_codes', 'jurisdiction_type')
        
    op.drop_index(op.f('ix_hoa_rules_hoa_name'), table_name='hoa_rules')
    op.drop_table('hoa_rules')



