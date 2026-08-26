import os
from dream_worker import parse_short_term_memory

def test_chore045():
    filepath = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/short_term_memory.jsonl"
    
    print("Testing CHORE-045: Parsing short_term_memory.jsonl")
    
    # Check if file exists physically
    if not os.path.exists(filepath):
        print("FAIL: short_term_memory.jsonl does not exist.")
        exit(1)
        
    print("File exists. Parsing...")
    memories = parse_short_term_memory(filepath)
    
    if len(memories) != 2:
        print(f"FAIL: Expected 2 memories, got {len(memories)}")
        exit(1)
        
    if memories[0]['id'] != '1':
        print("FAIL: Memory 1 ID mismatch.")
        exit(1)
        
    print("SUCCESS: CHORE-045 verification passed. Successfully read and parsed JSONL entries into memory objects.")

if __name__ == "__main__":
    test_chore045()
