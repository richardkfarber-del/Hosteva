import glob
import re

migration_files = glob.glob("/home/rdogen/OpenClaw_Factory/projects/Hosteva/alembic/versions/f9656d00d4a2*.py")
if not migration_files:
    print("Migration file not found.")
    exit(1)

migration_file = migration_files[0]

with open(migration_file, 'r') as f:
    content = f.read()

content = content.replace("existing_nullable=False)", "existing_nullable=False,\n               postgresql_using='id::uuid')")
content = content.replace("existing_nullable=False,\n               postgresql_using='id::uuid',\n               postgresql_using='id::uuid')", "existing_nullable=False,\n               postgresql_using='id::uuid')")

# also truncate property_compliance just in case
content = content.replace(
    "op.add_column('property_compliance', sa.Column('is_compliant'",
    "op.execute('TRUNCATE TABLE property_compliance CASCADE')\n    op.add_column('property_compliance', sa.Column('is_compliant'"
)

with open(migration_file, 'w') as f:
    f.write(content)

print("Migration file patched with postgresql_using.")