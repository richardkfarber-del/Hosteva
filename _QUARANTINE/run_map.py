import os
import subprocess

files = []
for d in ['app', 'frontend', 'backend']:
    for root, _, filenames in os.walk(d):
        for f in filenames:
            if '__pycache__' not in root and not f.endswith('.pyc'):
                files.append(os.path.join(root, f))

cmd = [
    "/home/rdogen/OpenClaw_Factory/projects/Hosteva/.venv/bin/aider",
    "--model", "gemini/gemini-2.5-flash",
    "--message", "Please analyze the provided files from the app/, frontend/, and backend/ directories. Write a comprehensive architecture and file map of these directories to REPO_MAP.md.",
    "--yes"
] + files

subprocess.run(cmd, cwd="/home/rdogen/OpenClaw_Factory/projects/Hosteva")
