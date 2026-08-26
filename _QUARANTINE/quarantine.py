import os
import shutil

whitelist = {
    'app',
    '.git',
    '.gitignore',
    'Dockerfile',
    'requirements.txt',
    'README.md',
    'quarantine.py',
    'quarantine_dryrun.py',
    '_QUARANTINE'
}

root_dir = os.path.dirname(os.path.abspath(__file__))
quarantine_dir = os.path.join(root_dir, '_QUARANTINE')

if not os.path.exists(quarantine_dir):
    os.makedirs(quarantine_dir)

items = os.listdir(root_dir)
for item in items:
    if item in whitelist:
        continue
    
    src = os.path.join(root_dir, item)
    dst = os.path.join(quarantine_dir, item)
    
    print(f"Moving: {item}")
    try:
        shutil.move(src, dst)
    except Exception as e:
        print(f"Error moving {item}: {e}")

print("Quarantine completed successfully.")
