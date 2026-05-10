import os
import chromadb
import sys

def main():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
    print(f"Initializing ChromaDB at {db_path}...")
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name="project_history")

    # Core project context files to ingest
    files_to_ingest = [
        "PROJECT_BOARD.md",
        "PIPELINE_ARCHITECTURE.md",
        "AGENTS.md",
        "SOUL.md",
        "IDENTITY.md",
        "GRAPHBIT_RESEARCH.md",
        "PHASED_WORKFLOW_PLAN.md"
    ]

    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    for file_name in files_to_ingest:
        file_path = os.path.join(base_dir, file_name)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                # We use the filename as the ID
                collection.upsert(
                    documents=[content],
                    metadatas=[{"source": file_name}],
                    ids=[file_name]
                )
            print(f"[SUCCESS] Ingested {file_name} into vector store.")
        else:
            print(f"[SKIPPED] {file_name} (File not found)")

    print("\nVector ingestion complete. ChromaDB is primed.")

if __name__ == "__main__":
    main()
