import re
import glob

migration_files = glob.glob("/home/rdogen/OpenClaw_Factory/projects/Hosteva/alembic/versions/f9656d00d4a2*.py")
if not migration_files:
    print("Migration file not found.")
    exit(1)

migration_file = migration_files[0]

with open(migration_file, 'r') as f:
    content = f.read()

trigger_sql = """
    op.execute('''
    CREATE OR REPLACE FUNCTION enforce_append_only_compliance()
    RETURNS TRIGGER AS $$
    BEGIN
        IF TG_OP = 'UPDATE' THEN
            RAISE EXCEPTION 'Cannot modify historical compliance records. Append-only temporal versioning enforced.';
        END IF;
        IF TG_OP = 'DELETE' THEN
            RAISE EXCEPTION 'Cannot delete compliance records. Append-only temporal versioning enforced.';
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_close_expired_compliance ON property_compliance;
    CREATE TRIGGER trg_close_expired_compliance
    BEFORE UPDATE OR DELETE ON property_compliance
    FOR EACH ROW EXECUTE FUNCTION enforce_append_only_compliance();
    ''')
"""

downgrade_sql = """
    op.execute('DROP TRIGGER IF EXISTS trg_close_expired_compliance ON property_compliance;')
    op.execute('DROP FUNCTION IF EXISTS enforce_append_only_compliance();')
"""

content = content.replace("    # ### end Alembic commands ###", trigger_sql + "    # ### end Alembic commands ###", 1)

downgrade_block = content.find("def downgrade() -> None:")
downgrade_end = content.find("    # ### end Alembic commands ###", downgrade_block)

content = content[:downgrade_end] + downgrade_sql + content[downgrade_end:]

with open(migration_file, 'w') as f:
    f.write(content)

print("Migration file patched.")
