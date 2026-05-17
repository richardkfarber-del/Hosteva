import asyncio
import sqlite3
import time
import httpx
from fastapi import FastAPI, Request

app = FastAPI()

def setup_db():
    conn = sqlite3.connect("test_concurrency.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS webhooks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        payload TEXT
                    )''')
    conn.commit()
    conn.close()

def insert_webhook(payload: str):
    conn = None
    try:
        conn = sqlite3.connect("test_concurrency.db", timeout=5.0) 
        cursor = conn.cursor()
        cursor.execute("INSERT INTO webhooks (payload) VALUES (?)", (payload,))
        conn.commit()
    except sqlite3.OperationalError as e:
        print(f"OperationalError caught gracefully: {e}")
    finally:
        if conn:
            conn.close()

@app.post("/webhook")
async def handle_webhook(request: Request):
    payload = await request.json()
    await asyncio.to_thread(insert_webhook, str(payload))
    return {"status": "ok"}

async def simulate_concurrent_webhooks(num_requests=100):
    setup_db()
    
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        start_time = time.time()
        
        tasks = [
            client.post("/webhook", json={"event": f"evt_{i}"})
            for i in range(num_requests)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for r in results if isinstance(r, httpx.Response) and r.status_code == 200)
        errors = [r for r in results if isinstance(r, Exception)]
        
        duration = time.time() - start_time
        
        print(f"Total Requests: {num_requests}")
        print(f"Successful: {success_count}")
        print(f"Failed: {len(errors)}")
        print(f"Duration: {duration:.2f}s")
        
        conn = sqlite3.connect("test_concurrency.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM webhooks")
        count = cursor.fetchone()[0]
        conn.close()
        
        print(f"DB Record Count: {count}")

if __name__ == "__main__":
    asyncio.run(simulate_concurrent_webhooks(200))
