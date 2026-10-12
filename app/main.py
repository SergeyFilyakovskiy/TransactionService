from contextlib import AsyncExitStack, asynccontextmanager

from fastapi import FastAPI

from app.api.error_handling import register_exception_handlers
from app.api.v1.routers import v1_router
from app.infrastructure.redis.redis_client import redis_lifespan
from app.infrastructure.s3.s3_client import s3_lifespan


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncExitStack() as stack:
        await stack.enter_async_context(redis_lifespan(app))
        await stack.enter_async_context(s3_lifespan(app))
        yield


app = FastAPI(
    version="0.1.0",
    title="Transaction service",
    lifespan=lifespan,
)

register_exception_handlers(app)
app.include_router(v1_router)


@app.get("/")
async def health():
    return {"status": "healthy"}
