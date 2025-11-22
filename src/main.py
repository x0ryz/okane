import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from src.auth.routes import router as auth_router
from src.transactions.routes import router as transactions_router
from src.categories.routes import router as categories_router
from src.statistics.routes import router as statistics_router
from src.config import settings

logger = logging.getLogger("uvicorn")


async def setup_redis_client() -> Redis:
    redis_client = Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        decode_responses=True
    )

    try:
        await redis_client.ping()
        logger.info("Redis connected successfully.")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")

    return redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis_client = await setup_redis_client()

    yield

    await app.state.redis_client.close()
    logger.info("Redis connection closed.")

app = FastAPI(title="Okane API", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(transactions_router)
app.include_router(categories_router)
app.include_router(statistics_router)