import re

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Let's just make sure the get_url logic is exactly as needed.
    # It already is, so we'll just rewrite it to itself to be safe.
    with open(filepath, 'w') as f:
        f.write(content)

fix_file('alembic/env.py')
fix_file('app/database.py')
