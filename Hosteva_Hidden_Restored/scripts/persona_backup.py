#!/usr/bin/env python3
import os
import sys
import shutil
import hashlib
import time
import filecmp

def get_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def main():
    base_dir = "/home/rdogen/OpenClaw_Factory/projects/Hosteva"
    agents_dir = os.path.join(base_dir, "agents")
    backups_base = os.path.join(base_dir, "backups")
    
    timestamp = time.strftime("%Y%md_%H%M%S")
    backup_dir = os.path.join(backups_base, f"personas_{timestamp}")
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    print(f"Starting Persona Backup and Safe Migration...")
    print(f"Target backup directory: {backup_dir}")

    # Gather source files (identity/persona files)
    target_files = ["IDENTITY.md", "SOUL.md", "STYLE.md", "AGENTS.md"]
    source_files = []
    
    for root, _, files in os.walk(agents_dir):
        for file in files:
            if file in target_files or file.endswith(".md"): # To be safe, just backup all MD files in agents
                source_files.append(os.path.join(root, file))

    if not source_files:
        print("No persona files found.")
        sys.exit(0)

    # 1. Generate SHA-256 manifest BEFORE copying
    print("Generating pre-copy SHA-256 manifest...")
    manifest = {}
    for filepath in source_files:
        rel_path = os.path.relpath(filepath, agents_dir)
        manifest[rel_path] = get_sha256(filepath)
    
    manifest_path = os.path.join(backup_dir, "manifest_pre.txt")
    with open(manifest_path, "w") as f:
        for rel_path, checksum in manifest.items():
            f.write(f"{checksum}  {rel_path}\n")

    print(f"Manifest created with {len(manifest)} files.")

    # 2. Copy files
    print("Copying files to isolated backup directory...")
    for filepath in source_files:
        rel_path = os.path.relpath(filepath, agents_dir)
        dest_path = os.path.join(backup_dir, rel_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(filepath, dest_path)

    # 3. Post-copy checksum validation & QA byte-for-byte verification
    print("Validating post-copy checksums and byte-for-byte integrity...")
    validation_failed = False
    
    for rel_path, original_checksum in manifest.items():
        original_filepath = os.path.join(agents_dir, rel_path)
        copied_filepath = os.path.join(backup_dir, rel_path)
        
        if not os.path.exists(copied_filepath):
            print(f"ERROR: File missing after copy: {rel_path}")
            validation_failed = True
            continue
            
        new_checksum = get_sha256(copied_filepath)
        
        if original_checksum != new_checksum:
            print(f"ERROR: Checksum mismatch for {rel_path}!")
            print(f"Expected: {original_checksum}")
            print(f"Got:      {new_checksum}")
            validation_failed = True
        
        # QA validation: mathematically defined as byte-for-byte text-diffing
        if not filecmp.cmp(original_filepath, copied_filepath, shallow=False):
            print(f"ERROR: Byte-for-byte diff failed for {rel_path}")
            validation_failed = True

    if validation_failed:
        print("CRITICAL ERROR: Migration failed QA validation. Data corruption detected.")
        sys.exit(1)
    
    print("SUCCESS: Post-copy checksums match perfectly. 100% of original bytes survived in the destination.")
    print("Migration phase 1 complete.")

if __name__ == "__main__":
    main()
