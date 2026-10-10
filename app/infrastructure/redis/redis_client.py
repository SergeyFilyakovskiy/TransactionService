from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import ConnectionPool, Redis

from app.core.config import settings


@asynccontextmanager
async def redis_lifespan(app: FastAPI):
    pool = ConnectionPool.from_url(
        url=settings.redis_url,
        max_connections=20,
        decode_responses=False,
    )
    app.state.redis = Redis(
        connection_pool=pool,
    )

    await app.state.redis.ping()
    try:
        yield
    finally:
        await app.state.redis.aclose()
