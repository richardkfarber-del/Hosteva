import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import async_session_maker

logger = logging.getLogger(__name__)

async def process_queue():
    async with async_session_maker() as session:
        # Fetch a pending job
        result = await session.execute(
            text("SELECT id, payload FROM jobs WHERE status = 'PENDING' FOR UPDATE SKIP LOCKED LIMIT 1")
        )
        job = result.fetchone()
        
        if not job:
            return
            
        job_id, payload = job
        
        try:
            # Mark as RUNNING
            await session.execute(
                text("UPDATE jobs SET status = 'RUNNING' WHERE id = :id"),
                {"id": job_id}
            )
            await session.commit()
            
            # Dummy processing
            logger.info(f"Processing job {job_id} with payload {payload}")
            await asyncio.sleep(1)
            
            # Mark as COMPLETED
            await session.execute(
                text("UPDATE jobs SET status = 'COMPLETED' WHERE id = :id"),
                {"id": job_id}
            )
            await session.commit()
            logger.info(f"Job {job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            await session.rollback()
            await session.execute(
                text("UPDATE jobs SET status = 'FAILED' WHERE id = :id"),
                {"id": job_id}
            )
            await session.commit()

async def start_worker_daemon():
    logger.info("Starting worker daemon...")
    while True:
        try:
            await process_queue()
        except Exception as e:
            logger.error(f"Worker loop error: {e}")
        await asyncio.sleep(5)