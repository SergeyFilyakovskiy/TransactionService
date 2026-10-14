from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import Balance
from app.domain.exceptions import BalanceNotFoundError
from app.domain.interfaces import IBalanceRepo


@dataclass(frozen=True)
class GetBalanceQuery:
    user_id: UUID
    currency_id: UUID


class GetBalanceHandler:

    def __init__(self, balance_repo: IBalanceRepo):
        self.balance_repo = balance_repo

    async def execute(self, query: GetBalanceQuery) -> Balance:
        balance = await self.balance_repo.get_by_user_and_currency(
            user_id=query.user_id,
            currency_id=query.currency_id,
        )

        if balance is None:
            raise BalanceNotFoundError()

        return balance
