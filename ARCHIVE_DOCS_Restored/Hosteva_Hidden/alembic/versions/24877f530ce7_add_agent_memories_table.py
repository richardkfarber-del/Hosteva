"""Add agent_memories table for CHORE-036

Revision ID: 24877f530ce7
Revises: cae7caeedc2f
Create Date: 2026-04-19 14:25:47.933087

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import pgvector

# revision identifiers, used by Alembic.
revision: str = '24877f530ce7'
down_revision: Union[str, Sequence[str], None] = 'cae7caeedc2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Create agent_memories with pgvector HNSW index."""
    op.create_table('agent_memories',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('agent_id', sa.String(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('embedding', pgvector.sqlalchemy.vector.VECTOR(dim=768), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_agent_memories_embedding_hnsw', 'agent_memories', ['embedding'], unique=False, postgresql_using='hnsw', postgresql_with={'m': 16, 'ef_construction': 64}, postgresql_ops={'embedding': 'vector_cosine_ops'})


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_agent_memories_embedding_hnsw', table_name='agent_memories', postgresql_using='hnsw', postgresql_with={'m': 16, 'ef_construction': 64}, postgresql_ops={'embedding': 'vector_cosine_ops'})
    op.drop_table('agent_memories')
