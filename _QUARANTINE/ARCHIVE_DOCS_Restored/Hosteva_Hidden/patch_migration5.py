import glob

migration_files = glob.glob("/home/rdogen/OpenClaw_Factory/projects/Hosteva/alembic/versions/cae7caeedc2f*.py")
if not migration_files:
    print("Migration file not found.")
    exit(1)

migration_file = migration_files[0]

upgrade_block = """def upgrade() -> None:
    # Drop in correct order
    op.execute('DROP TABLE IF EXISTS compliance_rules CASCADE;')
    op.execute('DROP TABLE IF EXISTS zoning_codes CASCADE;')
    op.execute('DROP TABLE IF EXISTS regions CASCADE;')
    op.execute('DROP TABLE IF EXISTS property_compliance CASCADE;')
    op.execute('DROP TABLE IF EXISTS municipal_codes CASCADE;')
    
    op.create_table('municipal_codes',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('municipality_name', sa.String(length=100), nullable=False),
    sa.Column('ordinance_number', sa.String(length=50), nullable=False),
    sa.Column('str_prohibited', sa.Boolean(), nullable=True),
    sa.Column('max_occupancy_limit', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.CheckConstraint('length(municipality_name) > 0', name='chk_mun_name_length'),
    sa.CheckConstraint("ordinance_number ~ '^[A-Z0-9-]+$'", name='chk_ordinance_format')
    )
    
    op.create_table('property_compliance',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('property_id', sa.UUID(), nullable=False),
    sa.Column('municipal_code_id', sa.UUID(), nullable=False),
    sa.Column('is_compliant', sa.Boolean(), nullable=False),
    sa.Column('violation_notes', sa.String(length=500), nullable=True),
    sa.Column('valid_period', postgresql.TSTZRANGE(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['municipal_code_id'], ['municipal_codes.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_property_compliance_valid_period', 'property_compliance', ['property_id', 'valid_period'], unique=False, postgresql_using='gist')

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

with open(migration_file, 'r') as f:
    content = f.read()

import re
content = re.sub(r'def upgrade\(\) -> None:.*?(?=def downgrade\(\) -> None:)', upgrade_block + '\n\n', content, flags=re.DOTALL)

with open(migration_file, 'w') as f:
    f.write(content)

print("Migration file replaced completely.")
