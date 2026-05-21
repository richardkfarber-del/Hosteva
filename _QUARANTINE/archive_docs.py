import os
import shutil

base_dir = '/home/rdogen/OpenClaw_Factory/projects/Hosteva'
archive_dir = os.path.join(base_dir, 'ARCHIVE_DOCS')
os.makedirs(archive_dir, exist_ok=True)

keep_files = {
    'MASTER_ROADMAP.md', 'SPRINT_BACKLOG.md', 'README.md', 'AGENTS.md', 
    'IDENTITY.md', 'SOUL.md', 'TOOLS.md', 'USER.md', 'MEMORY.md', 
    'REPO_MAP.md', 'PIPELINE_ARCHITECTURE.md'
}

for item in os.listdir(base_dir):
    item_path = os.path.join(base_dir, item)
    if os.path.isfile(item_path) and item.endswith('.md') and item not in keep_files:
        shutil.move(item_path, os.path.join(archive_dir, item))

for d in ['Hosteva_Hidden', 'sprint_13_archive']:
    d_path = os.path.join(base_dir, d)
    if os.path.exists(d_path) and os.path.isdir(d_path):
        shutil.move(d_path, os.path.join(archive_dir, d))

print('Archive complete.')
