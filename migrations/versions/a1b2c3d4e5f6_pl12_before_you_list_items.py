"""PL-12: before_you_list_items for Free Covered interactive checklist

Revision ID: a1b2c3d4e5f6
Revises: f1a2b3c4d5e6
Create Date: 2026-09-08
"""
from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "f1a2b3c4d5e6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if "before_you_list_items" in insp.get_table_names():
        return
    op.create_table(
        "before_you_list_items",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("property_id", sa.String(), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("item_key", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("is_complete", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("property_id", "item_key", name="uq_byl_property_item_key"),
    )
    op.create_index("ix_before_you_list_items_property_id", "before_you_list_items", ["property_id"])


def downgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if "before_you_list_items" not in insp.get_table_names():
        return
    op.drop_index("ix_before_you_list_items_property_id", table_name="before_you_list_items")
    op.drop_table("before_you_list_items")
