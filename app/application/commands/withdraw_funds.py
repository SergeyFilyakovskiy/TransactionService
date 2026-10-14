from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import TransactionType
from app.domain.entities import Transaction
from app.domain.exceptions import (
    BalanceNotFoundError,
    CurrencyNotFoundError,
    UserNotFoundError,
)
from app.domain.interfaces import (
    IBalanceRepo,
    ICurrencyRepo,
    ITransactionRepo,
    IUserRepo,
)
from app.domain.value_objects import Amount


@dataclass(frozen=True)
class WithdrawFundsCommand:
    user_id: UUID
    currency_id: UUID
    amount: float | str


class WithdrawFundsHandler:
    def __init__(
        self,
        session: AsyncSession,
        user_repo: IUserRepo,
        balance_repo: IBalanceRepo,
        currency_repo: ICurrencyRepo,
        transaction_repo: ITransactionRepo,
    ):
        self.session = session
        self.user_repo = user_repo
        self.balance_repo = balance_repo
        self.currency_repo = currency_repo
        self.transaction_repo = transaction_repo

    async def execute(self, command: WithdrawFundsCommand) -> Transaction:
        user = await self.user_repo.get_by_id(command.user_id)

        if user is None:
            raise UserNotFoundError()

        user.check_not_frozen()

        currency = await self.currency_repo.get_by_id(command.currency_id)

        if currency is None:
            raise CurrencyNotFoundError()

        balance = await self.balance_repo.get_for_update(
            user_id=command.user_id,
            currency_id=command.currency_id,
        )

        if balance is None:
            raise BalanceNotFoundError()

        transaction = Transaction.create(
            user_id=command.user_id,
            currency_id=command.currency_id,
            amount=Amount(Decimal(str(command.amount))),
            transaction_type=TransactionType.WITHDRAWAL,
        )

        balance.debit(transaction.amount)

        transaction.mark_completed()

        await self.balance_repo.save(balance)
        await self.transaction_repo.save(transaction)
        await self.session.commit()

        return transaction
