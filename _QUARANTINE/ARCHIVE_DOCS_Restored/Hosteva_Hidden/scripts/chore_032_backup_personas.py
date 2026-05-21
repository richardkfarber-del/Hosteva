import os
import shutil
import hashlib
import time
import glob

def hash_file(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def main():
    base_dir = "/home/rdogen/OpenClaw_Factory/projects/Hosteva"
    agents_dir = os.path.join(base_dir, "agents")
    backup_dir = os.path.join(base_dir, "backups", f"personas_{int(time.time())}")
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir, exist_ok=True)
        
    print(f"Starting Persona Backup to: {backup_dir}")
    
    # 1. Route all backups and gather targets
    target_files = []
    for root, dirs, files in os.walk(agents_dir):
        for file in files:
            if file in ["SOUL.md", "STYLE.md", "IDENTITY.md"]:
                target_files.append(os.path.join(root, file))
                
    if not target_files:
        print("No persona files found.")
        return

    # 2. Generate SHA-256 checksum manifest of source files BEFORE copying
    pre_copy_manifest = {}
    for filepath in target_files:
        pre_copy_manifest[filepath] = hash_file(filepath)
        print(f"PRE-COPY HASH: {pre_copy_manifest[filepath]} - {filepath}")
        
    # 3. Copy files
    post_copy_manifest = {}
    for filepath in target_files:
        rel_path = os.path.relpath(filepath, agents_dir)
        dest_path = os.path.join(backup_dir, rel_path)
        
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(filepath, dest_path)
        
        # 4. Generate post-copy checksums
        post_copy_manifest[dest_path] = hash_file(dest_path)
        print(f"POST-COPY HASH: {post_copy_manifest[dest_path]} - {dest_path}")
        
    # Validation: mathematically defined as byte-for-byte matching (hash diffing)
    print("Validating checksums...")
    all_match = True
    for filepath, original_hash in pre_copy_manifest.items():
        rel_path = os.path.relpath(filepath, agents_dir)
        dest_path = os.path.join(backup_dir, rel_path)
        new_hash = post_copy_manifest[dest_path]
        
        if original_hash != new_hash:
            print(f"MISMATCH DETECTED: {filepath}")
            all_match = False
            
    if all_match:
        print("SUCCESS: 100% of the original bytes survived in the destination. Validation complete.")
    else:
        print("FAILURE: Hash mismatch.")
        raise Exception("Checksum validation failed!")

if __name__ == "__main__":
    main()
