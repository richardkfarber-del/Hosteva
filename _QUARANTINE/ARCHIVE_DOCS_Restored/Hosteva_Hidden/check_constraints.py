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
                    SELECT conname, pg_get_constraintdef(c.oid)
                    FROM pg_constraint c
                    JOIN pg_namespace n ON n.oid = c.connamespace
                    WHERE c.conrelid = 'municipal_codes'::regclass;
                """)
                print("Constraints:", cur.fetchall())
    except Exception as e:
        print("DB ERROR:", e)

if __name__ == "__main__":
    main()
