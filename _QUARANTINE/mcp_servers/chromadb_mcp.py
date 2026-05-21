import json
import sys
import chromadb
import os

# A lightweight Python wrapper to act as the local ChromaDB tool for the swarm

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection(name="project_history")

def query_vectors(query_text, n_results=3):
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    return json.dumps(results)

def ingest_vectors(text, source_id):
    collection.upsert(
        documents=[text],
        metadatas=[{"source": source_id}],
        ids=[source_id]
    )
    return json.dumps({"status": "success", "source": source_id})

if __name__ == "__main__":
    # Basic CLI routing for GraphBit to call via shell/subprocess
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing command. Use 'query' or 'ingest'."}))
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "query":
        print(query_vectors(sys.argv[2]))
    elif command == "ingest":
        print(ingest_vectors(sys.argv[2], sys.argv[3]))
    else:
        print(json.dumps({"error": f"Unknown command: {command}"}))
