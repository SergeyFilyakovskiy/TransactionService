from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import Transaction
from app.domain.exceptions import TransactionNotFoundError
from app.domain.interfaces import ITransactionRepo


@dataclass(frozen=True)
class GetTransactionQuery:
    transaction_id: UUID


class GetTransactionHandler:

    def __init__(self, transaction_repo: ITransactionRepo):
        self.transaction_repo = transaction_repo

    async def execute(self, query: GetTransactionQuery) -> Transaction:
        transaction = await self.transaction_repo.get_by_id(query.transaction_id)

        if transaction is None:
            raise TransactionNotFoundError()

        return transaction
