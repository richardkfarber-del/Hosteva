import os
import redis.asyncio as redis

# Vibranium Habit: Dynamically load connection string and enforce TLS in production
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

if os.getenv("ENVIRONMENT") == "production" and REDIS_URL.startswith("redis://"):
    # Enforce secure transit for caching layer
    REDIS_URL = REDIS_URL.replace("redis://", "rediss://", 1)

# Create an async connection pool
pool = redis.ConnectionPool.from_url(REDIS_URL)

async def get_redis() -> redis.Redis:
    """Dependency to yield a Redis client from the pool."""
    client = redis.Redis.from_pool(pool)
    try:
        yield client
    finally:
        await client.aclose()
