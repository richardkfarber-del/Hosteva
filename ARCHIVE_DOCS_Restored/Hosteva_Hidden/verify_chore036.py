import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.models.memory import AgentMemory
from alembic.config import Config
from alembic.script import ScriptDirectory

def verify_models():
    # Verify AgentMemory fields
    assert hasattr(AgentMemory, 'id'), "Missing id column"
    assert hasattr(AgentMemory, 'agent_id'), "Missing agent_id column"
    assert hasattr(AgentMemory, 'content'), "Missing content column"
    assert hasattr(AgentMemory, 'metadata_'), "Missing metadata column"
    assert hasattr(AgentMemory, 'embedding'), "Missing embedding column"
    
    # Verify table args (Index)
    indexes = AgentMemory.__table_args__
    assert len(indexes) > 0, "No indexes defined"
    hnsw_index = indexes[0]
    assert hnsw_index.name == 'ix_agent_memories_embedding_hnsw'
    assert hnsw_index.dialect_options['postgresql']['using'] == 'hnsw'
    print("[SUCCESS] AgentMemory model verified.")

def verify_alembic():
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)
    revisions = [rev.revision for rev in script.walk_revisions()]
    assert '24877f530ce7' in revisions, "Missing CHORE-036 Alembic revision"
    print("[SUCCESS] Alembic migration verified.")

if __name__ == "__main__":
    verify_models()
    verify_alembic()
    print("[SUCCESS] Local verification passed.")
