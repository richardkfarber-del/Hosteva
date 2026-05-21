import time
import os

log_file = '/home/rdogen/OpenClaw_Factory/projects/Hosteva/swarm_terminal.log'
backlog_file = '/home/rdogen/OpenClaw_Factory/projects/Hosteva/SPRINT_BACKLOG.md'
venv_python = '/home/rdogen/OpenClaw_Factory/projects/Hosteva/venv/bin/python'
project_dir = '/home/rdogen/OpenClaw_Factory/projects/Hosteva'

def log(msg):
    with open(log_file, 'a') as f:
        f.write(msg + '\n')

while True:
    try:
        with open(backlog_file, 'r') as f:
            content = f.read()
    except:
        time.sleep(3)
        continue
        
    if 'EXECUTIVE SIGN-OFF GRANTED' in content:
        log('\n🚀 PHASE 1 TRIGGERED: Executing Intake & Architecture...')
        os.system(f'{venv_python} {project_dir}/run_phase1.py >> {log_file} 2>&1')
        log('🏁 PHASE 1 COMPLETE. Artifact saved. Awaiting Audit...\n')
        
    elif 'PHASE 1 AUDIT' in content:
        log('\n🛡️ AUDIT TRIGGERED: Agent Coulson reviewing Phase 1...')
        os.system(f'{venv_python} {project_dir}/run_audit1.py >> {log_file} 2>&1')
        log('🏁 AUDIT COMPLETE. Check backlog for next status...\n')
        
    time.sleep(5)
