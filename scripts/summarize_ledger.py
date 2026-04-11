#!/usr/bin/env python3
import sys

def summarize(file_path):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        if len(lines) > 200:
            summary = lines[:100] + ["\n... [CONTENT TRUNCATED FOR CONTEXT OVERFLOW PROTECTION] ...\n\n"] + lines[-100:]
        else:
            summary = lines
            
        print("".join(summary))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    summarize(sys.argv[1])
