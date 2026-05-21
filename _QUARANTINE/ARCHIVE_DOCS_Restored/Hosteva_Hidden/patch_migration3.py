import glob

migration_files = glob.glob("/home/rdogen/OpenClaw_Factory/projects/Hosteva/alembic/versions/f9656d00d4a2*.py")
if not migration_files:
    print("Migration file not found.")
    exit(1)

migration_file = migration_files[0]

with open(migration_file, 'r') as f:
    content = f.read()

content = content.replace(
    "op.add_column('municipal_codes', sa.Column('municipality_name'",
    "op.execute('TRUNCATE TABLE municipal_codes CASCADE')\n    op.add_column('municipal_codes', sa.Column('municipality_name'"
)

with open(migration_file, 'w') as f:
    f.write(content)

print("Migration file patched with TRUNCATE.")