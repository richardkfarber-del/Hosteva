import sqlite3
import os

def migrate_db(db_path):
    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist. Skipping.")
        return
        
    print(f"Migrating database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Turn off foreign key constraints temporarily
    cursor.execute("PRAGMA foreign_keys = OFF;")
    
    # 2. Get existing table info
    cursor.execute("PRAGMA table_info(municipal_codes)")
    cols_info = cursor.fetchall()
    columns = [col[1] for col in cols_info]
    
    # 3. Read existing data
    cursor.execute("SELECT * FROM municipal_codes")
    existing_rows = cursor.fetchall()
    
    # Map index to column name
    col_mapping = {idx: col for idx, col in enumerate(columns)}
    
    # 4. Rename old table
    cursor.execute("DROP TABLE IF EXISTS municipal_codes_old;")
    cursor.execute("ALTER TABLE municipal_codes RENAME TO municipal_codes_old;")
    
    # 5. Create new table
    cursor.execute("""
    CREATE TABLE municipal_codes (
        id CHAR(36) PRIMARY KEY,
        municipality_name VARCHAR(100) NOT NULL,
        ordinance_number VARCHAR(50) NOT NULL,
        str_prohibited BOOLEAN DEFAULT 0,
        max_occupancy_limit INTEGER,
        stay_restriction_days INTEGER,
        max_rentals_per_year INTEGER,
        requires_permit BOOLEAN DEFAULT 0,
        permit_name VARCHAR(100),
        source_url VARCHAR(255),
        tax_rate FLOAT,
        is_allowed BOOLEAN DEFAULT 1,
        zoning_code VARCHAR(50),
        property_type VARCHAR(50),
        rejection_reason VARCHAR(255),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        jurisdiction_type VARCHAR(50),
        str_permitted_raw VARCHAR(100),
        permit_required_raw VARCHAR(50),
        minimum_stay_requirement VARCHAR(255),
        occupancy_limits VARCHAR(255),
        tax_rate_registration_fee VARCHAR(255),
        last_verified_date DATE,
        state VARCHAR(50),
        is_ai_scraped BOOLEAN DEFAULT 0 NOT NULL,
        is_expert_verified BOOLEAN DEFAULT 0 NOT NULL,
        scraped_at DATETIME,
        form_template_path VARCHAR(500),
        form_layout_json TEXT,
        CONSTRAINT chk_mun_name_length CHECK (length(municipality_name) > 0),
        CONSTRAINT uq_municipal_codes_name_type_state UNIQUE (municipality_name, jurisdiction_type, state)
    );
    """)
    
    # 6. Copy rows back, populating default values for new columns
    new_cols = [
        "id", "municipality_name", "ordinance_number", "str_prohibited", "max_occupancy_limit",
        "stay_restriction_days", "max_rentals_per_year", "requires_permit", "permit_name",
        "source_url", "tax_rate", "is_allowed", "zoning_code", "property_type", "rejection_reason",
        "created_at", "updated_at", "jurisdiction_type", "str_permitted_raw", "permit_required_raw",
        "minimum_stay_requirement", "occupancy_limits", "tax_rate_registration_fee",
        "last_verified_date", "state", "is_ai_scraped", "is_expert_verified", "scraped_at",
        "form_template_path", "form_layout_json"
    ]
    
    for row in existing_rows:
        row_dict = {col_mapping[idx]: val for idx, val in enumerate(row)}
        
        # Add defaults/fallbacks for new fields
        if "state" not in row_dict or row_dict["state"] is None:
            row_dict["state"] = "FL"  # All existing seed rules are Florida-based
        if "is_ai_scraped" not in row_dict:
            row_dict["is_ai_scraped"] = 0
        if "is_expert_verified" not in row_dict:
            row_dict["is_expert_verified"] = 1  # Existing seed rules are expert verified
        if "scraped_at" not in row_dict:
            row_dict["scraped_at"] = None
        if "form_template_path" not in row_dict:
            row_dict["form_template_path"] = None
        if "form_layout_json" not in row_dict:
            row_dict["form_layout_json"] = None
            
        col_list = []
        val_list = []
        for col in new_cols:
            if col in row_dict:
                col_list.append(col)
                val_list.append(row_dict[col])
                
        placeholders = ", ".join(["?"] * len(col_list))
        stmt = f"INSERT INTO municipal_codes ({', '.join(col_list)}) VALUES ({placeholders})"
        cursor.execute(stmt, val_list)
        
    # 7. Drop old table
    cursor.execute("DROP TABLE municipal_codes_old;")
    
    # 8. Re-enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    conn.close()
    print(f"Successfully migrated {db_path}")

if __name__ == "__main__":
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    migrate_db(os.path.join(project_dir, "hosteva.db"))
    migrate_db(os.path.join(project_dir, "test.db"))
