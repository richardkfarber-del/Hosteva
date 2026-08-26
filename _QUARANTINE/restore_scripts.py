import os
import glob
import shutil

source_dir = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/deprecated_wrappers"
target_dir = "/home/rdogen/OpenClaw_Factory/projects/Hosteva"

count = 0
for file in glob.glob(f"{source_dir}/*"):
    try:
        shutil.move(file, target_dir)
        count += 1
    except Exception as e:
        print(f"Error moving {file}: {e}")

print(f"Restored {count} scripts.")
