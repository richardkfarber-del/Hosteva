import uuid
from sqlalchemy import Column, String, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
from app.database import Base

class AgentMemory(Base):
    """
    SQLAlchemy model for storing agent memories with pgvector embeddings.
    Satisfies CHORE-036: Define Embeddings Table Schema.
    Validating schema structure and enforcing index parameters.
    """
    __tablename__ = "agent_memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSONB, nullable=False, default=dict)
    embedding = Column(Vector(768))

    __table_args__ = (
        Index(
            'ix_agent_memories_embedding_hnsw',
            'embedding',
            postgresql_using='hnsw',
            postgresql_with={'m': 16, 'ef_construction': 64},
            postgresql_ops={'embedding': 'vector_cosine_ops'}
        ),
    )
