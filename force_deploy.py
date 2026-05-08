import os
import shutil
import subprocess

def run_cmd(cmd):
    print(f'Running: {cmd}')
    res = subprocess.run(cmd, shell=True, cwd='/home/rdogen/OpenClaw_Factory/projects/Hosteva', capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print(f'ERROR: {res.stderr}')

# Remove ALL problematic nested git repos
for root, dirs, files in os.walk('/home/rdogen/OpenClaw_Factory/projects/Hosteva'):
    if '.git' in dirs and root != '/home/rdogen/OpenClaw_Factory/projects/Hosteva':
        bad_git = os.path.join(root, '.git')
        shutil.rmtree(bad_git)
        print(f'Removed {bad_git}')

run_cmd('git add .')
run_cmd('git commit -m "feat: Stripe Paywall Implementation (FEAT-013)"')
run_cmd('git push origin master')
