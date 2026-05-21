import os

whitelist = {
    'app',
    '.git',
    '.gitignore',
    'Dockerfile',
    'requirements.txt',
    'README.md',
    'quarantine_dryrun.py',
    'quarantine.py',
    '_QUARANTINE'
}

root_dir = os.path.dirname(os.path.abspath(__file__))
items = os.listdir(root_dir)

to_move = []
kept = []

for item in items:
    if item in whitelist:
        kept.append(item)
    else:
        to_move.append(item)

print("--- KEPT (WHITELISTED) ---")
for item in sorted(kept):
    print(f"  {item}")

print("\n--- TO MOVE TO _QUARANTINE ---")
for item in sorted(to_move):
    print(f"  {item}")
