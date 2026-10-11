from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities import Currency


class ICurrencyRepo(ABC):

    @abstractmethod
    async def save(self, currency: Currency) -> None:
        """Create or update currency."""
        ...

    @abstractmethod
    async def get_by_id(self, currency_id: UUID) -> Currency | None: ...

    @abstractmethod
    async def get_by_code(self, code: str) -> Currency | None: ...

    @abstractmethod
    async def list(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Currency]: ...

    @abstractmethod
    async def delete(self, currency_id: UUID) -> None: ...

    @abstractmethod
    async def exists_by_code(self, code: str) -> bool: ...
