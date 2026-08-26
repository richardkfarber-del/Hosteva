import os
try:
    import chromadb
except ImportError:
    print("ChromaDB not installed")
    exit(1)

def main():
    db_path = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/chroma_db"
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name="hosteva_context")
    
    files_to_ingest = [
        "00_context_backend.md",
        "00_context_frontend.md",
        "00_context_planning.md",
        "00_context_compliance.md",
        "00_context_marketing.md",
        "PROJECT_BOARD.md",
        "SPIKE_FEAT-013.md"
    ]
    
    for idx, filename in enumerate(files_to_ingest):
        filepath = os.path.join("/home/rdogen/OpenClaw_Factory/projects/Hosteva", filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                collection.upsert(
                    documents=[content],
                    metadatas=[{"source": filename}],
                    ids=[f"doc_{idx}"]
                )
            print(f"Ingested {filename}")
        else:
            print(f"File not found: {filepath}")
            
    print("Ingestion complete.")

if __name__ == "__main__":
    main()
