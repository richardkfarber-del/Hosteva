"""EPIC-RULES: research_requests + municipal_codes.source_kind

Revision ID: f1a2b3c4d5e6
Revises: c4a91e2b7d10
Create Date: 2026-09-06
"""
from alembic import op
import sqlalchemy as sa

revision = "f1a2b3c4d5e6"
down_revision = "c4a91e2b7d10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    cols = [c["name"] for c in insp.get_columns("municipal_codes")] if "municipal_codes" in insp.get_table_names() else []
    if "source_kind" not in cols:
        op.add_column("municipal_codes", sa.Column("source_kind", sa.String(length=50), nullable=True))

    if "research_requests" not in insp.get_table_names():
        op.create_table(
            "research_requests",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("jurisdiction_key", sa.String(length=255), nullable=False),
            sa.Column("state", sa.String(length=10), nullable=False),
            sa.Column("municipality_name", sa.String(length=150), nullable=False),
            sa.Column("jurisdiction_type", sa.String(length=50), nullable=True),
            sa.Column("sample_address", sa.String(length=255), nullable=True),
            sa.Column("host_id", sa.String(), nullable=True),
            sa.Column("status", sa.String(length=50), nullable=False),
            sa.Column("trigger_reason", sa.String(length=100), nullable=True),
            sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
            sa.Column("hit_count", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("draft_municipal_code_id", sa.String(length=36), nullable=True),
            sa.Column("draft_payload", sa.Text(), nullable=True),
            sa.Column("worker_notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("jurisdiction_key", name="uq_research_requests_jurisdiction_key"),
        )
        op.create_index("ix_research_requests_jurisdiction_key", "research_requests", ["jurisdiction_key"])
        op.create_index("ix_research_requests_status", "research_requests", ["status"])


def downgrade() -> None:
    op.drop_table("research_requests")
    try:
        op.drop_column("municipal_codes", "source_kind")
    except Exception:
        pass
