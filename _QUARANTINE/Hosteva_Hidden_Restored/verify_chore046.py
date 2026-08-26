import os
import sys

def verify():
    worker_path = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/dream_worker.py"
    if not os.path.exists(worker_path):
        print("❌ dream_worker.py not found.")
        return
        
    with open(worker_path, "r") as f:
        content = f.read()
        
    if "nomic-embed-text" in content and "api/embeddings" in content:
        print("✅ Ollama nomic-embed-text integration found.")
    else:
        print("❌ Missing Ollama embedding generation logic.")
        
    if "INSERT INTO agent_memories" in content and "embedding" in content:
        print("✅ DB insertion logic for agent_memories found.")
    else:
        print("❌ Missing pgvector agent_memories insertion logic.")

if __name__ == "__main__":
    verify()
