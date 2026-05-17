import json
import os

def parse_short_term_memory(filepath):
    memories = []
    if not os.path.exists(filepath):
        print(f"File {filepath} not found.")
        return memories
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                memories.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Error parsing line: {line}. Error: {e}")
                
    return memories

if __name__ == "__main__":
    test_filepath = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/short_term_memory.jsonl"
    parsed = parse_short_term_memory(test_filepath)
    print(f"Parsed {len(parsed)} memories.")
    for m in parsed:
        print(m)
