import glob

migration_files = glob.glob("/home/rdogen/OpenClaw_Factory/projects/Hosteva/alembic/versions/cae7caeedc2f*.py")
if not migration_files:
    print("Migration file not found.")
    exit(1)

migration_file = migration_files[0]

with open(migration_file, 'r') as f:
    content = f.read()

content = content.replace("sa.Column('property_id', sa.UUID(), nullable=False)", "sa.Column('property_id', sa.String(), nullable=False)")

with open(migration_file, 'w') as f:
    f.write(content)

print("Migration file patched for property_id type.")