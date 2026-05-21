import subprocess
import sys
import os

log_file = open('swarm_loop.log', 'w')
process = subprocess.Popen(
    ['bash', 'start_loop.sh'],
    stdout=log_file,
    stderr=subprocess.STDOUT,
    cwd='/home/rdogen/OpenClaw_Factory/projects/Hosteva',
    start_new_session=True
)
print(f'Swarm restarted via Python with PID {process.pid}')
