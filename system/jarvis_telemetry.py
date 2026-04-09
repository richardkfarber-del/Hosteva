#!/usr/bin/env python3
import os
import time
import random
import subprocess

def get_gpu_load():
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'],
            capture_output=True, text=True
        )
        if result.stdout.strip():
            return int(result.stdout.strip().split('\n')[0])
    except Exception:
        pass
    # Simulate if nvidia-smi fails
    return random.randint(10, 95)

def main():
    print("Jarvis Telemetry Daemon started...")
    current_model = ""
    while True:
        gpu_load = get_gpu_load()
        # Simulate active ticket load (20% chance of heavy load)
        ticket_heavy = random.random() > 0.8
        
        if gpu_load > 75 or ticket_heavy:
            new_model = "google/gemini-3.1-pro-preview"
            print(f"Spike detected! GPU: {gpu_load}%, Heavy Ticket: {ticket_heavy}. Shifting to Gemini...")
        else:
            new_model = "ollama/qwen2.5-coder:7b"
            print(f"Load nominal. GPU: {gpu_load}%, Heavy Ticket: {ticket_heavy}. Shifting to local Qwen...")
            
        if new_model != current_model:
            os.system(f"openclaw config set agents.defaults.model {new_model}")
            current_model = new_model
            
        time.sleep(30)

if __name__ == "__main__":
    main()
