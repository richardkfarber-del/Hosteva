import os
import glob

base_path = '/home/rdogen/OpenClaw_Factory/projects/Hosteva'
files_to_remove = glob.glob(os.path.join(base_path, '*artifact.md')) + [
    os.path.join(base_path, 'swarm_loop.log'), 
    os.path.join(base_path, 'daily_ledger.md'), 
    os.path.join(base_path, 'coulson_intervention_log.md')
]
for f in files_to_remove:
    if os.path.exists(f):
        try:
            os.remove(f)
            print(f"Removed {f}")
        except Exception as e:
            print(f"Failed to remove {f}: {e}")
