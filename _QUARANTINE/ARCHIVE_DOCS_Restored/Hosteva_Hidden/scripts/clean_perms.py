import os

base_dir = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents"
for root, dirs, files in os.walk(base_dir):
    for f in files:
        fpath = os.path.join(root, f)
        try:
            os.chmod(fpath, 0o664) # rw-rw-r--
        except Exception:
            pass
