import os
import shutil
import hashlib
import time
import json
import filecmp

PROJECT_ROOT = "/home/rdogen/OpenClaw_Factory/projects/Hosteva"
AGENTS_DIR = os.path.join(PROJECT_ROOT, "agents")
BACKUP_BASE = os.path.join(PROJECT_ROOT, "backups")

def get_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def main():
    if not os.path.exists(BACKUP_BASE):
        os.makedirs(BACKUP_BASE)
        
    timestamp = int(time.time())
    backup_dir = os.path.join(BACKUP_BASE, f"personas_{timestamp}")
    os.makedirs(backup_dir)
    
    print(f"Isolated timestamped directory created: {backup_dir}")
    
    manifest = {}
    
    # 1. Generate Pre-copy Manifest
    print("Generating SHA-256 pre-copy manifest...")
    for root, dirs, files in os.walk(AGENTS_DIR):
        for file in files:
            if file.endswith(".md"):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, AGENTS_DIR)
                manifest[rel_path] = get_sha256(filepath)
                
    manifest_path = os.path.join(backup_dir, "pre_copy_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=4)
        
    print(f"Pre-copy manifest generated with {len(manifest)} files.")
    
    # 2. Copy files
    print("Routing backups to isolated directory...")
    for rel_path in manifest.keys():
        src_path = os.path.join(AGENTS_DIR, rel_path)
        dest_path = os.path.join(backup_dir, rel_path)
        
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(src_path, dest_path)
        
    # 3. Post-copy checksum verification
    print("Verifying post-copy checksums...")
    post_copy_failures = 0
    for rel_path, expected_sha in manifest.items():
        dest_path = os.path.join(backup_dir, rel_path)
        actual_sha = get_sha256(dest_path)
        if actual_sha != expected_sha:
            print(f"ERROR: Checksum mismatch for {rel_path}!")
            post_copy_failures += 1
            
    if post_copy_failures > 0:
        print("MIGRATION HALTED: Post-copy checksums do not match pre-copy manifest.")
        exit(1)
        
    print("Checksum validation passed. 100% match.")
    
    # 4. QA Validation: Byte-for-byte text diffing
    print("Executing QA validation (byte-for-byte text diffing)...")
    qa_failures = 0
    for rel_path in manifest.keys():
        src_path = os.path.join(AGENTS_DIR, rel_path)
        dest_path = os.path.join(backup_dir, rel_path)
        
        if not filecmp.cmp(src_path, dest_path, shallow=False):
            print(f"QA ERROR: Byte-for-byte diff failed for {rel_path}!")
            qa_failures += 1
            
    if qa_failures > 0:
        print("MIGRATION HALTED: QA validation failed.")
        exit(1)
        
    print("QA validation successful. 100% of original bytes survived.")
    print("Persona State Backup and File Auditing Complete.")

if __name__ == "__main__":
    main()
