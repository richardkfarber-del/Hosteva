import sys
sys.path.insert(0, "/home/rdogen/OpenClaw_Factory/projects/Hosteva/.venv/lib/python3.10/site-packages")
try:
    import psycopg
except ImportError:
    sys.path.insert(0, "/home/rdogen/OpenClaw_Factory/projects/Hosteva/.venv/lib/python3.11/site-packages")
    import psycopg

def main():
    conn_info = "postgresql://postgres:postgres@localhost:5432/hosteva"
    try:
        with psycopg.connect(conn_info) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT trigger_name, event_manipulation, event_object_table
                    FROM information_schema.triggers
                    WHERE trigger_name = 'trg_close_expired_compliance';
                """)
                res = cur.fetchall()
                print("Triggers:", res)
                
                cur.execute("""
                    SELECT indexname, indexdef
                    FROM pg_indexes
                    WHERE tablename = 'property_compliance';
                """)
                print("Indexes:", cur.fetchall())
    except Exception as e:
        print("DB ERROR:", e)

if __name__ == "__main__":
    main()
