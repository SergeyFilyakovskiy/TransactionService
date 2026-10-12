from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.core.enums import TransactionStatus, TransactionType
from app.domain.entities import Transaction


class ITransactionRepo(ABC):

    @abstractmethod
    async def save(self, transaction: Transaction) -> None:
        """Create or update transaction."""
        ...

    @abstractmethod
    async def get_by_id(self, transaction_id: UUID) -> Transaction | None: ...

    @abstractmethod
    async def list_by_user(
        self,
        user_id: UUID,
        *,
        currency_id: UUID | None = None,
        status: TransactionStatus | None = None,
        transaction_type: TransactionType | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Transaction]: ...
