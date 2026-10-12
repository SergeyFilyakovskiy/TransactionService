from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Balance
from app.domain.interfaces.i_balance_repo import IBalanceRepo
from app.domain.value_objects import Amount
from app.infrastructure.postgres.models import BalanceORM


class BalanceRepository(IBalanceRepo):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, balance: Balance) -> None:
        orm = await self.session.get(BalanceORM, balance.id)

        if orm is None:
            orm = self._to_orm(balance)
            self.session.add(orm)
        else:
            orm.user_id = balance.user_id
            orm.currency_id = balance.currency_id
            orm.amount = balance.amount.value
            orm.updated_at = balance.updated_at

    async def get_by_id(self, balance_id: UUID) -> Balance | None:
        orm = await self.session.get(BalanceORM, balance_id)
        return self._to_entity(orm) if orm else None

    async def get_by_user_and_currency(
        self,
        user_id: UUID,
        currency_id: UUID,
    ) -> Balance | None:
        orm = await self.session.scalar(
            select(BalanceORM).where(
                BalanceORM.user_id == user_id,
                BalanceORM.currency_id == currency_id,
            )
        )

        return self._to_entity(orm) if orm else None

    async def get_for_update(
        self,
        user_id: UUID,
        currency_id: UUID,
    ) -> Balance | None:
        orm = await self.session.scalar(
            select(BalanceORM)
            .where(
                BalanceORM.user_id == user_id,
                BalanceORM.currency_id == currency_id,
            )
            .with_for_update()
        )

        return self._to_entity(orm) if orm else None

    async def list_by_user(
        self,
        user_id: UUID,
        currency_id: UUID | None = None,
    ) -> list[Balance]:
        stmt = select(BalanceORM).where(BalanceORM.user_id == user_id)

        if currency_id is not None:
            stmt = stmt.where(BalanceORM.currency_id == currency_id)

        stmt = stmt.order_by(BalanceORM.created_at)

        result = await self.session.scalars(stmt)

        return [self._to_entity(orm) for orm in result.all()]

    async def delete(self, balance_id: UUID) -> None:
        orm = await self.session.get(BalanceORM, balance_id)

        if orm:
            await self.session.delete(orm)

    def _to_entity(self, orm: BalanceORM) -> Balance:
        return Balance(
            id=orm.id,
            user_id=orm.user_id,
            currency_id=orm.currency_id,
            amount=Amount(orm.amount),
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    def _to_orm(self, balance: Balance) -> BalanceORM:
        return BalanceORM(
            id=balance.id,
            user_id=balance.user_id,
            currency_id=balance.currency_id,
            amount=balance.amount.value,
            created_at=balance.created_at,
            updated_at=balance.updated_at,
        )
