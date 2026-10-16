from dataclasses import dataclass
from uuid import UUID

from app.core.enums import TransactionStatus, TransactionType
from app.domain.entities import Transaction
from app.domain.interfaces import ITransactionRepo


@dataclass(frozen=True)
class ListTransactionsQuery:
    user_id: UUID
    currency_id: UUID | None = None
    status: TransactionStatus | None = None
    transaction_type: TransactionType | None = None
    limit: int = 100
    offset: int = 0


class ListTransactionsHandler:

    def __init__(self, transaction_repo: ITransactionRepo):
        self.transaction_repo = transaction_repo

    async def execute(self, query: ListTransactionsQuery) -> list[Transaction]:
        return await self.transaction_repo.list_by_user(
            user_id=query.user_id,
            currency_id=query.currency_id,
            status=query.status,
            transaction_type=query.transaction_type,
            limit=query.limit,
            offset=query.offset,
        )
