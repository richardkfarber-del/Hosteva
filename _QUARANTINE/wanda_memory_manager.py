import os
import shutil
import time
import glob

AGENTS_DIR = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents"
BACKUP_DIR = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/memory_backups"

def create_backups():
    print("WANDA: Initiating core memory backups...")
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = int(time.time())
    
    for agent in os.listdir(AGENTS_DIR):
        agent_path = os.path.join(AGENTS_DIR, agent)
        if os.path.isdir(agent_path):
            mem_file = os.path.join(agent_path, "CORE_MEMORY.md")
            if os.path.exists(mem_file):
                backup_name = f"{agent}_CORE_MEMORY_{timestamp}.md.bak"
                backup_path = os.path.join(BACKUP_DIR, backup_name)
                shutil.copy2(mem_file, backup_path)
                print(f"Backed up {agent} -> {backup_name}")

def purge_old_backups(days=3):
    print(f"\nWANDA: Sweeping for backups older than {days} days...")
    if not os.path.exists(BACKUP_DIR):
        return
        
    now = time.time()
    cutoff = now - (days * 86400)
    
    for backup_file in glob.glob(os.path.join(BACKUP_DIR, "*.bak")):
        file_mtime = os.path.getmtime(backup_file)
        if file_mtime < cutoff:
            os.remove(backup_file)
            print(f"Purged old backup: {os.path.basename(backup_file)}")

def main():
    create_backups()
    purge_old_backups(days=3)
    print("\nWANDA: Memory backup and purge complete. Ready for role-specific revisions.")

if __name__ == "__main__":
    main()
