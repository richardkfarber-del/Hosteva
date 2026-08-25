import sqlite3

def inspect_db(db_path):
    print(f"Inspecting {db_path}...")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in c.fetchall()]
    print("Tables:", tables)
    for table in tables:
        c.execute(f"PRAGMA table_info({table})")
        columns = c.fetchall()
        print(f"\nTable: {table}")
        for col in columns:
            print(f"  Column: {col[1]} ({col[2]})")
            
        c.execute(f"SELECT * FROM {table} LIMIT 5")
        rows = c.fetchall()
        print(f"  Rows (up to 5):")
        for row in rows:
            print(f"    {row}")
    conn.close()

if __name__ == "__main__":
    import sys
    db = "hosteva.db"
    if len(sys.argv) > 1:
        db = sys.argv[1]
    inspect_db(db)
