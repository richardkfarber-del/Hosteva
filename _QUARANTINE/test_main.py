import subprocess
import sys

try:
    res = subprocess.run(
        ["/home/rdogen/OpenClaw_Factory/projects/Hosteva/venv/bin/python", "-u", "/home/rdogen/OpenClaw_Factory/projects/Hosteva/workflow.py"],
        cwd="/home/rdogen/OpenClaw_Factory/projects/Hosteva",
        capture_output=True,
        text=True,
        timeout=3600
    )
    print("STDOUT:", res.stdout)
    print("STDERR:", res.stderr)
except subprocess.TimeoutExpired as e:
    print("TIMEOUT!")
    print("STDOUT SO FAR:", e.stdout.decode('utf-8') if isinstance(e.stdout, bytes) else e.stdout)
    print("STDERR SO FAR:", e.stderr.decode('utf-8') if isinstance(e.stderr, bytes) else e.stderr)
