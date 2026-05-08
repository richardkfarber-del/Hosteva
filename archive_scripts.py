import os
import glob
import shutil

target_dir = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/deprecated_wrappers"
os.makedirs(target_dir, exist_ok=True)

patterns = [
    "run_*.py", "fix_*.py", "patch*.py", "cleanup_*.py", "apply_*.py", 
    "test_*.py", "test_*.sh", "start_*.py", "start_*.sh", "rm_*.py", 
    "auto_fix_*.py", "build_missing_*.py", "check*.py", "clean_*.py", 
    "diagnose.py", "dispatch_*.py", "distribute_*.py", "extract_*.py", 
    "fury_kickoff.py", "halt_*.py", "inspect_*.py", "jarvis_*.py", 
    "loop.py", "refactor_*.py", "truncate_*.py", "update_*.py", 
    "wanda_*.py", "workflow.py"
]

count = 0
for pattern in patterns:
    for file in glob.glob(f"/home/rdogen/OpenClaw_Factory/projects/Hosteva/{pattern}"):
        try:
            shutil.move(file, target_dir)
            count += 1
        except Exception as e:
            pass

print(f"Archived {count} obsolete scripts.")
