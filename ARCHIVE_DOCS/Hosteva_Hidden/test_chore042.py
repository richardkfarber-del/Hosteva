import os
import sys
import psycopg

def test_chore042():
    try:
        conn_str = "postgresql://postgres:postgres@localhost:5432/hosteva"
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM agent_memories;")
                count = cur.fetchone()[0]
                
                if count > 0:
                    cur.execute("SELECT agent_id, metadata, embedding FROM agent_memories LIMIT 1;")
                    row = cur.fetchone()
                    print(f"VERIFIED: {count} records found in agent_memories.")
                    print(f"Sample Agent ID: {row[0]}")
                    print(f"Sample Metadata: {row[1]}")
                    
                    # Embedding is returned as a string representing a vector
                    if isinstance(row[2], str) and row[2].startswith('['):
                        print("VERIFIED: Embedding format is correct.")
                    else:
                        print(f"Embedding type: {type(row[2])}")
                else:
                    print("REJECTED: No records found in agent_memories.")
    except Exception as e:
        print(f"REJECTED: Exception during validation - {e}")

if __name__ == "__main__":
    test_chore042()