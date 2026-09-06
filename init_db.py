import os
from dotenv import load_dotenv
from sqlalchemy import text
from app.database import engine, Base

# Load environment variables
load_dotenv()

def main():
    print("Running standalone database initialization...")
    os.makedirs("app/static/property_images", exist_ok=True)
    try:
        # Explicitly import all database models so they register on Base
        import app.db_models
        import app.models.memory
        import app.models.host
        import app.models.property
        import app.models.zoning
        import app.models.job
        import app.models.compliance
        import app.models.swarm
        import app.models.oauth
        import app.models.password_reset
        import app.models.research_request
        import app.integrations.ota_models
        
        # Enable PostgreSQL extensions if PostgreSQL
        if "sqlite" not in str(engine.url):
            try:
                with engine.connect() as conn:
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gist;"))
                    conn.commit()
                print("pgvector and btree_gist extensions verified/created.")
            except Exception as e:
                print(f"Warning: Could not create database extensions (vector, btree_gist): {e}")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")

        # Check and add columns if missing
        from sqlalchemy import inspect
        inspector = inspect(engine)
        try:
            columns = [c["name"] for c in inspector.get_columns("properties")]
            for col_name in ["image_url", "required_permits", "local_restrictions", "airbnb_ical_import_url", "vrbo_ical_import_url", "hosteva_ical_export_token"]:
                if col_name not in columns:
                    with engine.connect() as conn:
                        if "sqlite" in str(engine.url):
                            conn.execute(text(f"ALTER TABLE properties ADD COLUMN {col_name} VARCHAR;"))
                        else:
                            conn.execute(text(f"ALTER TABLE properties ADD COLUMN IF NOT EXISTS {col_name} VARCHAR;"))
                        conn.commit()
                    print(f"Added {col_name} column to properties table.")
                else:
                    print(f"{col_name} column already exists in properties table.")
        except Exception as col_err:
            print(f"Warning: Could not check/add columns: {col_err}")

        # Check and add columns for property_compliance table
        try:
            columns = [c["name"] for c in inspector.get_columns("property_compliance")]
            for col_name, col_type in [
                ("status", "VARCHAR(50)"),
                ("rejection_notes", "VARCHAR(500)"),
                ("violation_notes", "VARCHAR(500)"),
                ("uploaded_file_url", "VARCHAR(500)"),
                ("ocr_metadata_json", "TEXT"),
                ("verification_notes", "TEXT"),
                ("task_name", "VARCHAR(255)")
            ]:
                if col_name not in columns:
                    with engine.connect() as conn:
                        if "sqlite" in str(engine.url):
                            conn.execute(text(f"ALTER TABLE property_compliance ADD COLUMN {col_name} {col_type};"))
                        else:
                            conn.execute(text(f"ALTER TABLE property_compliance ADD COLUMN IF NOT EXISTS {col_name} {col_type};"))
                        conn.commit()
                    print(f"Added {col_name} column to property_compliance table.")
                else:
                    print(f"{col_name} column already exists in property_compliance table.")
        except Exception as col_err:
            print(f"Warning: Could not check/add columns to property_compliance: {col_err}")

        # Check and add columns for municipal_codes table
        try:
            columns = [c["name"] for c in inspector.get_columns("municipal_codes")]
            for col_name, col_type in [
                ("state", "VARCHAR(50)"),
                ("is_ai_scraped", "BOOLEAN DEFAULT FALSE"),
                ("is_expert_verified", "BOOLEAN DEFAULT FALSE"),
                ("scraped_at", "TIMESTAMP"),
                ("form_template_path", "VARCHAR(500)"),
                ("form_layout_json", "TEXT"),
                ("jurisdiction_type", "VARCHAR(50)"),
                ("str_permitted_raw", "VARCHAR(100)"),
                ("permit_required_raw", "VARCHAR(50)"),
                ("minimum_stay_requirement", "VARCHAR(255)"),
                ("occupancy_limits", "VARCHAR(255)"),
                ("tax_rate_registration_fee", "VARCHAR(255)"),
                ("last_verified_date", "DATE"),
                ("source_kind", "VARCHAR(50)")
            ]:
                if col_name not in columns:
                    with engine.connect() as conn:
                        if "sqlite" in str(engine.url):
                            conn.execute(text(f"ALTER TABLE municipal_codes ADD COLUMN {col_name} {col_type};"))
                        else:
                            conn.execute(text(f"ALTER TABLE municipal_codes ADD COLUMN IF NOT EXISTS {col_name} {col_type};"))
                        conn.commit()
                    print(f"Added {col_name} column to municipal_codes table.")
                else:
                    print(f"{col_name} column already exists in municipal_codes table.")
        except Exception as col_err:
            print(f"Warning: Could not check/add columns to municipal_codes: {col_err}")


        # Ensure subscriptions columns for Essentials entitlement (US-006 simulate/webhook)
        try:
            sub_cols = [c["name"] for c in inspector.get_columns("subscriptions")]
            for col_name, col_type in [
                ("tier", "VARCHAR(100)"),
                ("plan_details", "VARCHAR"),
                ("stripe_customer_id", "VARCHAR"),
                ("stripe_subscription_id", "VARCHAR(255)"),
                ("status", "VARCHAR"),
                ("user_id", "VARCHAR"),
            ]:
                if col_name not in sub_cols:
                    with engine.connect() as conn:
                        if "sqlite" in str(engine.url):
                            conn.execute(text(f"ALTER TABLE subscriptions ADD COLUMN {col_name} {col_type};"))
                        else:
                            conn.execute(text(f"ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS {col_name} {col_type};"))
                        conn.commit()
                    print(f"Added {col_name} column to subscriptions table.")
                    sub_cols.append(col_name)
                else:
                    print(f"{col_name} column already exists in subscriptions table.")
        except Exception as sub_col_err:
            print(f"Warning: Could not check/add subscriptions columns: {sub_col_err}")

        try:
            tables = inspector.get_table_names()
            if "password_reset_tokens" not in tables:
                from app.models.password_reset import PasswordResetToken
                PasswordResetToken.__table__.create(bind=engine, checkfirst=True)
                print("Created password_reset_tokens table.")
            else:
                print("password_reset_tokens table already exists.")
        except Exception as prt_err:
            print(f"Warning: Could not ensure password_reset_tokens: {prt_err}")


        try:
            tables = inspector.get_table_names()
            if "research_requests" not in tables:
                from app.models.research_request import ResearchRequest
                ResearchRequest.__table__.create(bind=engine, checkfirst=True)
                print("Created research_requests table.")
            else:
                print("research_requests table already exists.")
        except Exception as rr_err:
            print(f"Warning: Could not ensure research_requests: {rr_err}")



        # Auto-seed GTM rules database if empty
        try:
            import sys
            scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "scripts"))
            if scripts_dir not in sys.path:
                sys.path.append(scripts_dir)

            from sqlalchemy import func
            from app.models.compliance import MunicipalCode
            try:
                from scripts.seed_rules import seed_rules
            except ImportError:
                from seed_rules import seed_rules
            from app.database import SessionLocal

            db_sess = SessionLocal()
            try:
                excel_dir = os.path.dirname(__file__)
                count = db_sess.query(func.count(MunicipalCode.id)).scalar()
                # SP-010: when Drive Complete.xlsx is present, always idempotent upsert
                # (fixes seed-if-empty footgun that left stale/partial DBs without denser rows).
                try:
                    from scripts.seed_rules import complete_xlsx_present
                except ImportError:
                    from seed_rules import complete_xlsx_present
                force_reseed = complete_xlsx_present(excel_dir)
                if count == 0 or force_reseed:
                    reason = "empty table" if count == 0 else "Complete.xlsx present (idempotent upsert)"
                    print(f"Running Excel rules seeding ({reason}; prior municipal_codes count={count})...")
                    seed_rules(db_sess, excel_dir)
                    print("Excel rules seeding completed successfully.")
                else:
                    print(
                        f"Database already contains {count} municipal code rules and Complete.xlsx "
                        "is absent. Skipping Excel auto-seeding."
                    )
            except Exception as seed_err:
                print(f"Warning: Auto-seeding failed: {seed_err}")
            finally:
                db_sess.close()

            # SP-001 / Free Audit: always upsert Miami Beach + related packs from
            # scripts/seed_compliance_rules.py (idempotent). Excel Phase-1 sheet does
            # not include City of Miami Beach; Render buildCommand runs init_db.py.
            try:
                try:
                    from scripts.seed_compliance_rules import seed_data as seed_compliance_packs
                except ImportError:
                    from seed_compliance_rules import seed_data as seed_compliance_packs
                print("Running seed_compliance_rules.py (Miami Beach Free Audit pack)...")
                seed_compliance_packs()
                print("seed_compliance_rules.py completed.")
            except Exception as pack_err:
                print(f"Warning: seed_compliance_rules pack failed: {pack_err}")
        except Exception as seed_init_err:
            print(f"Warning: Skipping auto-seeding step during database initialization: {seed_init_err}")

    except Exception as e:
        print(f"Error during database initialization: {e}")
        import traceback
        traceback.print_exc()
        # We raise the exception to exit with non-zero code and stop startup if DB init fails
        raise e

if __name__ == "__main__":
    try:
        from app.scripts.purge_sample_ordinances import purge_sample_ordinances
        purge_sample_ordinances()
    except Exception as _purge_err:
        print(f"Sample ordinance purge hook skipped: {_purge_err}")
    main()
