import asyncio
import logging
import json
from sqlalchemy import text
from app.database import SessionLocal
from app.db_models import QueueTask

logger = logging.getLogger(__name__)

class AsyncTaskQueue:
    def __init__(self):
        self.workers = []
        self.running = False

    async def enqueue(self, task_name, payload):
        with SessionLocal() as db:
            task = QueueTask(task_name=task_name, payload=json.dumps(payload), status="pending")
            db.add(task)
            db.commit()
            logger.info(f"Enqueued task {task_name}")

    async def worker(self, worker_id):
        while self.running:
            try:
                # Wrap sync DB calls in a thread if needed, but for now blocking is okay in a simplified queue
                with SessionLocal() as db:
                    sql = text("""
                        SELECT id, task_name, payload 
                        FROM queue_tasks 
                        WHERE status = 'pending' 
                        FOR UPDATE SKIP LOCKED 
                        LIMIT 1
                    """)
                    result = db.execute(sql).fetchone()
                    
                    if result:
                        task_id, task_name, payload = result
                        db.execute(text("UPDATE queue_tasks SET status = 'processing' WHERE id = :id"), {"id": task_id})
                        db.commit()
                        
                        logger.info(f"Worker {worker_id} executing task {task_name} (ID: {task_id})")
                        
                        # Simulate actual task execution (e.g., calling a registered function)
                        await asyncio.sleep(0.1)
                        
                        db.execute(text("UPDATE queue_tasks SET status = 'completed' WHERE id = :id"), {"id": task_id})
                        db.commit()
                    else:
                        await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)

    def start_workers(self, num_workers=3):
        self.running = True
        for i in range(num_workers):
            task = asyncio.create_task(self.worker(i))
            self.workers.append(task)

    async def stop_workers(self):
        self.running = False
        for task in self.workers:
            task.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)

task_queue = AsyncTaskQueue()
