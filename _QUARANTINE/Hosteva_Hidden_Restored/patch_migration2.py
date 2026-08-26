import glob

migration_files = glob.glob("/home/rdogen/OpenClaw_Factory/projects/Hosteva/alembic/versions/f9656d00d4a2*.py")
if not migration_files:
    print("Migration file not found.")
    exit(1)

migration_file = migration_files[0]

with open(migration_file, 'r') as f:
    content = f.read()

content = content.replace("    op.drop_table('compliance_rules')\n    op.drop_table('regions')\n    op.drop_table('zoning_codes')", "    op.drop_table('compliance_rules')\n    op.drop_table('zoning_codes')\n    op.drop_table('regions')")

with open(migration_file, 'w') as f:
    f.write(content)

print("Migration file drop order fixed.")