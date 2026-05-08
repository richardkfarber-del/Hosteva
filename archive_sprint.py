import os
import shutil
import glob

base_dir = '/home/rdogen/OpenClaw_Factory/projects/Hosteva'
archive_dir = os.path.join(base_dir, 'sprint_13_archive')
os.makedirs(archive_dir, exist_ok=True)

files_to_move = glob.glob(os.path.join(base_dir, '*_artifact.md')) + \
                [os.path.join(base_dir, f) for f in ['SPRINT_BACKLOG.md', 'SPIKE_FEAT-013.md', 'daily_ledger.md', 'strike_counter.txt', 'coulson_intervention_log.md']]

for f in files_to_move:
    if os.path.exists(f):
        shutil.move(f, os.path.join(archive_dir, os.path.basename(f)))

# Also wipe the sqlite databases to clear the ghosts
for db in glob.glob(os.path.join(base_dir, '*.sqlite')) + glob.glob(os.path.join(base_dir, '*.db')):
    if os.path.exists(db):
        shutil.move(db, os.path.join(archive_dir, os.path.basename(db)))

# Recreate empty files
with open(os.path.join(base_dir, 'daily_ledger.md'), 'w') as f: f.write('')
with open(os.path.join(base_dir, 'strike_counter.txt'), 'w') as f: f.write('0')
with open(os.path.join(base_dir, 'coulson_intervention_log.md'), 'w') as f: f.write('')

print('Archive complete.')
