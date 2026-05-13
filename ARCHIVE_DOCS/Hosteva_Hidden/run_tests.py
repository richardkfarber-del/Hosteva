import urllib.request
import json
import threading
import time
import subprocess

def run_tests():
    try:
        req = urllib.request.Request("http://127.0.0.1:8000/health")
        with urllib.request.urlopen(req) as response:
            print("Health check status:", response.status)
            print("Health check body:", response.read().decode())
    except Exception as e:
        print("Test failed:", e)

print("Starting tests (skipping uvicorn start as we will just test the live Render app instead for API if local fails)")
