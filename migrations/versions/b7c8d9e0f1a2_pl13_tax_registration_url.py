"""PL-13 / TE-013: municipal_codes.tax_registration_url

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2026-09-09
"""
from alembic import op
import sqlalchemy as sa

revision = "b7c8d9e0f1a2"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if "municipal_codes" not in insp.get_table_names():
        return
    cols = [c["name"] for c in insp.get_columns("municipal_codes")]
    if "tax_registration_url" not in cols:
        op.add_column(
            "municipal_codes",
            sa.Column("tax_registration_url", sa.String(length=500), nullable=True),
        )


def downgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if "municipal_codes" not in insp.get_table_names():
        return
    cols = [c["name"] for c in insp.get_columns("municipal_codes")]
    if "tax_registration_url" in cols:
        op.drop_column("municipal_codes", "tax_registration_url")
