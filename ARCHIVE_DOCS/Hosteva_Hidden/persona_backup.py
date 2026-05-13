import os
import shutil
import hashlib
import time
import json
import filecmp
from pathlib import Path

AGENTS_DIR = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents"
BACKUP_ROOT = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/backups"

def get_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def main():
    if not os.path.exists(AGENTS_DIR):
        print(f"Error: Agents directory {AGENTS_DIR} does not exist.")
        return

    # 1. Route to isolated timestamped directory
    timestamp = str(int(time.time()))
    backup_dir = os.path.join(BACKUP_ROOT, f"persona_backup_{timestamp}")
    os.makedirs(backup_dir, exist_ok=True)
    
    print(f"Starting backup to: {backup_dir}")

    # Find all identity files (assuming .md in agents directory)
    agent_files = []
    for root, _, files in os.walk(AGENTS_DIR):
        for file in files:
            if file.endswith(".md"):
                agent_files.append(os.path.join(root, file))

    if not agent_files:
        print("No agent files found.")
        return

    # 2. Generate SHA-256 checksum manifest BEFORE copying
    pre_manifest = {}
    for f in agent_files:
        pre_manifest[f] = get_sha256(f)

    manifest_path = os.path.join(backup_dir, "pre_copy_manifest.json")
    with open(manifest_path, "w") as mf:
        json.dump(pre_manifest, mf, indent=2)
    print("Pre-copy manifest generated successfully.")

    # 3. Copy files
    for src in agent_files:
        rel_path = os.path.relpath(src, AGENTS_DIR)
        dest = os.path.join(backup_dir, rel_path)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(src, dest)

    # 4. Post-copy checksums and verification
    post_manifest = {}
    verification_failed = False
    
    for src in agent_files:
        rel_path = os.path.relpath(src, AGENTS_DIR)
        dest = os.path.join(backup_dir, rel_path)
        
        post_hash = get_sha256(dest)
        post_manifest[dest] = post_hash
        
        # Byte-for-byte text diffing / QA validation
        if pre_manifest[src] != post_hash:
            print(f"FATAL: Checksum mismatch for {src} -> {dest}")
            verification_failed = True
        
        if not filecmp.cmp(src, dest, shallow=False):
            print(f"FATAL: Byte-for-byte diff failed for {src} -> {dest}")
            verification_failed = True

    if verification_failed:
        print("HALT: Post-copy checksums or byte-diffs do not perfectly match the pre-copy manifest.")
        exit(1)
    
    print("SUCCESS: 100% of original bytes survived. Backup verified mathematically.")
    print("Migration phase 1 complete. Proceeding to next phase...")

if __name__ == "__main__":
    main()
