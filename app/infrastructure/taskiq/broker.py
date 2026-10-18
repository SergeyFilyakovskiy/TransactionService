from __future__ import annotations

from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from app.core.config import settings

broker = ListQueueBroker(url=settings.taskiq_broker_url).with_result_backend(
    RedisAsyncResultBackend(redis_url=settings.taskiq_result_backend_url)
)
