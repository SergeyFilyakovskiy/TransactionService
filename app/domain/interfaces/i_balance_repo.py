from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities import Balance


class IBalanceRepo(ABC):

    @abstractmethod
    async def save(self, balance: Balance) -> None:
        """Create or update balance."""
        ...

    @abstractmethod
    async def get_by_id(self, balance_id: UUID) -> Balance | None: ...

    @abstractmethod
    async def get_by_user_and_currency(
        self,
        user_id: UUID,
        currency_id: UUID,
    ) -> Balance | None: ...

    @abstractmethod
    async def get_for_update(
        self,
        user_id: UUID,
        currency_id: UUID,
    ) -> Balance | None:
        """Get balance with row lock."""
        ...

    @abstractmethod
    async def list_by_user(
        self,
        user_id: UUID,
        currency_id: UUID | None = None,
    ) -> list[Balance]: ...

    @abstractmethod
    async def delete(self, balance_id: UUID) -> None: ...
