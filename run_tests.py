import os, subprocess
env = os.environ.copy()
env['PYTHONPATH'] = '/home/rdogen/OpenClaw_Factory/projects/Hosteva'
res = subprocess.run(['/home/rdogen/OpenClaw_Factory/projects/Hosteva/venv/bin/pytest', 'tests/'], env=env, cwd='/home/rdogen/OpenClaw_Factory/projects/Hosteva', capture_output=True, text=True)
print(res.stdout)
print(res.stderr)
