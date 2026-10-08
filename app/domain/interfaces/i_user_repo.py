from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities import User


class IUserRepo(ABC):

    # ── User CRUD ─────────────────────────────────────────

    @abstractmethod
    async def save(self, user: User) -> None:
        """Create or update user."""
        ...

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def delete(self, user_id: UUID) -> None: ...

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool: ...
