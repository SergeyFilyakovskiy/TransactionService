from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import Balance
from app.domain.interfaces import IBalanceRepo


@dataclass(frozen=True)
class ListBalancesQuery:
    user_id: UUID
    currency_id: UUID | None = None


class ListBalancesHandler:

    def __init__(self, balance_repo: IBalanceRepo):
        self.balance_repo = balance_repo

    async def execute(self, query: ListBalancesQuery) -> list[Balance]:
        return await self.balance_repo.list_by_user(
            user_id=query.user_id,
            currency_id=query.currency_id,
        )
