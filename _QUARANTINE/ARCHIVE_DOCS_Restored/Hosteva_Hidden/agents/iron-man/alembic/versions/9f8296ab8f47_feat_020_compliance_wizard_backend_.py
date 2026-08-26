"""FEAT-020: Compliance Wizard Backend Models

Revision ID: 9f8296ab8f47
Revises: 
Create Date: 2026-04-18 09:46:51.265787

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9f8296ab8f47'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('CREATE EXTENSION IF NOT EXISTS btree_gist;')
    op.create_table('municipal_codes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code_identifier', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.CheckConstraint("code_identifier ~ '^[A-Z0-9]{3,10}-[A-Z0-9]{2,10}$'", name='ck_municipal_code_format'),
    sa.CheckConstraint('length(code_identifier) <= 50', name='ck_municipal_code_length'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_municipal_codes_id'), 'municipal_codes', ['id'], unique=False)
    op.create_table('property_compliance',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('property_id', sa.Integer(), nullable=False),
    sa.Column('municipal_code_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('valid_period', postgresql.TSTZRANGE(), nullable=False),
    sa.CheckConstraint("status IN ('COMPLIANT', 'NON_COMPLIANT', 'PENDING')", name='ck_property_compliance_status'),
    sa.ForeignKeyConstraint(['municipal_code_id'], ['municipal_codes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_property_compliance_id'), 'property_compliance', ['id'], unique=False)
    op.create_index('ix_property_compliance_prop_period', 'property_compliance', ['property_id', 'valid_period'], unique=False, postgresql_using='gist')

    op.execute('''
        CREATE OR REPLACE FUNCTION trg_close_expired_compliance_func()
        RETURNS TRIGGER AS $$
        BEGIN
            IF TG_OP = 'UPDATE' THEN
                IF OLD.status != NEW.status OR OLD.property_id != NEW.property_id OR OLD.municipal_code_id != NEW.municipal_code_id THEN
                    RAISE EXCEPTION 'Historical overwrite operation prevented by trg_close_expired_compliance. Append-only allowed.';
                END IF;
            END IF;
            IF TG_OP = 'DELETE' THEN
                RAISE EXCEPTION 'Historical overwrite operation prevented by trg_close_expired_compliance. Deletes not allowed.';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    ''')
    op.execute('''
        CREATE TRIGGER trg_close_expired_compliance
        BEFORE UPDATE OR DELETE ON property_compliance
        FOR EACH ROW
        EXECUTE FUNCTION trg_close_expired_compliance_func();
    ''')

def downgrade() -> None:
    """Downgrade schema."""
    op.execute('DROP TRIGGER IF EXISTS trg_close_expired_compliance ON property_compliance')
    op.execute('DROP FUNCTION IF EXISTS trg_close_expired_compliance_func()')
    op.drop_index('ix_property_compliance_prop_period', table_name='property_compliance', postgresql_using='gist')
    op.drop_index(op.f('ix_property_compliance_id'), table_name='property_compliance')
    op.drop_table('property_compliance')
    op.drop_index(op.f('ix_municipal_codes_id'), table_name='municipal_codes')
    op.drop_table('municipal_codes')
