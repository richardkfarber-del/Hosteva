import os
import datetime

LEDGER_PATH = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/daily_ledger.md"
ARCHIVE_DIR = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/memory/archives"

def archive_ledger():
    if not os.path.exists(LEDGER_PATH):
        return
    
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    today = datetime.date.today().isoformat()
    archive_path = os.path.join(ARCHIVE_DIR, f"ledger_archive_{today}.md")
    
    with open(LEDGER_PATH, 'r') as f:
        content = f.read()
        
    with open(archive_path, 'a') as f:
        f.write(content + "\n\n")

if __name__ == "__main__":
    archive_ledger()
    print("Ledger archived successfully.")
