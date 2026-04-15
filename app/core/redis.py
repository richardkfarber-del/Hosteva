import redis.asyncio as redis

# Create an async connection pool to the redis host specified in docker-compose
pool = redis.ConnectionPool.from_url("redis://redis:6379")

async def get_redis() -> redis.Redis:
    """Dependency to yield a Redis client from the pool."""
    client = redis.Redis.from_pool(pool)
    try:
        yield client
    finally:
        await client.aclose()
