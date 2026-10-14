from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import TransactionType
from app.domain.entities import Transaction
from app.domain.exceptions import (
    BalanceNotFoundError,
    TransactionAlreadyCancelledError,
    TransactionNotFoundError,
    UserNotFoundError,
)
from app.domain.interfaces import IBalanceRepo, ITransactionRepo, IUserRepo


@dataclass(frozen=True)
class CancelTransactionCommand:
    transaction_id: UUID
    cancelled_by_user_id: UUID


class CancelTransactionHandler:
    def __init__(
        self,
        session: AsyncSession,
        user_repo: IUserRepo,
        balance_repo: IBalanceRepo,
        transaction_repo: ITransactionRepo,
    ):
        self.session = session
        self.user_repo = user_repo
        self.balance_repo = balance_repo
        self.transaction_repo = transaction_repo

    async def execute(self, command: CancelTransactionCommand) -> Transaction:
        transaction = await self.transaction_repo.get_by_id(command.transaction_id)

        if transaction is None:
            raise TransactionNotFoundError()

        if transaction.is_cancelled:
            raise TransactionAlreadyCancelledError()

        if transaction.user_id != command.cancelled_by_user_id:
            raise TransactionNotFoundError()

        user = await self.user_repo.get_by_id(command.cancelled_by_user_id)

        if user is None:
            raise UserNotFoundError()

        user.check_not_frozen()

        balance = await self.balance_repo.get_for_update(
            user_id=transaction.user_id,
            currency_id=transaction.currency_id,
        )

        if balance is None:
            raise BalanceNotFoundError()

        cancellation = Transaction.create(
            user_id=transaction.user_id,
            currency_id=transaction.currency_id,
            amount=transaction.amount,
            transaction_type=(
                TransactionType.DEPOSIT
                if transaction.is_withdrawal
                else TransactionType.WITHDRAWAL
            ),
        )

        if transaction.is_withdrawal:
            balance.credit(transaction.amount)
        else:
            balance.debit(transaction.amount)

        transaction.mark_cancelled(cancelled_by_transaction_id=cancellation.id)
        cancellation.mark_completed()
        cancellation.set_cancellation_reference(transaction.id)

        await self.balance_repo.save(balance)
        await self.transaction_repo.save(transaction)
        await self.transaction_repo.save(cancellation)
        await self.session.commit()

        return cancellation
