import os
import glob

files_to_delete = [
    '/home/rdogen/OpenClaw_Factory/projects/Hosteva/Hosteva_Hidden/planning/TECH-001_lobster_pipe.md',
    '/home/rdogen/OpenClaw_Factory/projects/Hosteva/Hosteva_Hidden/fix_heimdall_lobster.py',
    '/home/rdogen/OpenClaw_Factory/projects/Hosteva/Hosteva_Hidden/LOBSTER.md',
    '/home/rdogen/OpenClaw_Factory/projects/Hosteva/Hosteva_Hidden/scripts/lobster_interceptor.py',
    '/home/rdogen/OpenClaw_Factory/projects/Hosteva/Hosteva_Hidden/scripts/lobster_daemon.py',
    '/home/rdogen/OpenClaw_Factory/projects/Hosteva/Hosteva_Hidden/scripts/lobster.sh',
    '/home/rdogen/OpenClaw_Factory/projects/Hosteva/Hosteva_Hidden/lobster.md',
    '/home/rdogen/OpenClaw_Factory/projects/Hosteva/Hosteva_Hidden/infrastructure/LOBSTER.md'
]

for f in files_to_delete:
    if os.path.exists(f):
        os.remove(f)
        print(f'Deleted: {f}')

print('\nAgents:')
for a in os.listdir('/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents'):
    print(a)

print('\nContext files:')
for c in glob.glob('/home/rdogen/OpenClaw_Factory/projects/Hosteva/00_context_*.md'):
    print(c)
