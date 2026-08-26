import subprocess

def run_cmd(cmd):
    print(f'Running: {cmd}')
    res = subprocess.run(cmd, shell=True, cwd='/home/rdogen/OpenClaw_Factory/projects/Hosteva', capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print(f'ERROR: {res.stderr}')

run_cmd('git rm --cached openclaw-state.tgz')
run_cmd('git commit --amend -m "feat: Stripe Paywall Implementation (FEAT-013) - without large state file"')
run_cmd('git push origin master')
