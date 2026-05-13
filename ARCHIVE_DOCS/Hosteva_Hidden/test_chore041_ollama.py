import requests
import json

def test_ollama_chunker():
    url = "http://127.0.0.1:11434/api/embeddings"
    payload = {
        "model": "nomic-embed-text",
        "prompt": "This is a chunked text string to test the API."
    }
    
    try:
        response = requests.post(url, json=payload, timeout=3600)
        if response.status_code == 200:
            data = response.json()
            if "embedding" in data and isinstance(data["embedding"], list) and isinstance(data["embedding"][0], float):
                print("VERIFIED")
            else:
                print("REJECTED: Invalid response format")
        else:
            print(f"REJECTED: status code {response.status_code}")
    except Exception as e:
        print(f"REJECTED: {e}")

if __name__ == "__main__":
    test_ollama_chunker()
