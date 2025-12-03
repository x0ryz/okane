import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from src.auth.routes import router as auth_router
from src.transactions.routes import router as transactions_router
from src.categories.routes import router as categories_router
from src.statistics.routes import router as statistics_router
from src.redis_utils import init_redis, close_redis
from src.mq import broker

logger = logging.getLogger("uvicorn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    logger.info("Redis connected successfully.")
    await broker.connect()
    logger.info("FastStream connected successfully.")

    yield

    await broker.close()
    logger.info("FastStream connection closed.")
    await close_redis()
    logger.info("Redis connection closed.")

app = FastAPI(title="Okane API", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(transactions_router)
app.include_router(categories_router)
app.include_router(statistics_router)

add_pagination(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://okane.x0ryz.cc"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)