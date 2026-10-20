"""
Точка входа taskiq-воркера.

Запуск:
    taskiq worker worker:broker
"""

from app.infrastructure.taskiq import tasks  # noqa
from app.infrastructure.taskiq.broker import broker

__all__ = ["broker"]
