import urllib.request
import sys

try:
    req = urllib.request.Request('http://localhost:11434/api/tags')
    with urllib.request.urlopen(req, timeout=3600) as response:
        print("Ollama is responding:", response.status)
except Exception as e:
    print("Ollama connection failed:", str(e))
