import os
import shutil

base_dir = "/home/rdogen/OpenClaw_Factory/projects/Hosteva"
backup_dir = os.path.join(base_dir, "db_backup")
os.makedirs(backup_dir, exist_ok=True)

files_to_move = [
    "memory/brain.db",
    ".openclaw-madcloser/tasks/runs.sqlite",
    "03_planning_poker_artifact.md"
]

for f in files_to_move:
    src = os.path.join(base_dir, f)
    if os.path.exists(src):
        shutil.move(src, os.path.join(backup_dir, os.path.basename(f)))

with open(os.path.join(base_dir, "daily_ledger.md"), "w") as f:
    f.write("")

with open(os.path.join(base_dir, "strike_counter.txt"), "w") as f:
    f.write("0")

print("Cleanup complete. Ghost databases isolated.")
