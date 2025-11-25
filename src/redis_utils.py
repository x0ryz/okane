from redis import asyncio as aioredis
from src.config import settings

redis_client: aioredis.Redis | None = None

async def init_redis():
    global redis_client
    redis_client = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        encoding="utf-8",
        decode_responses=True
    )

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()

async def get_redis_client():
    return redis_client