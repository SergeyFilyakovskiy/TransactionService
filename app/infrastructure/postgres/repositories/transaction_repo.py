from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import TransactionStatus, TransactionType
from app.domain.entities import Transaction
from app.domain.interfaces.i_transaction_repo import ITransactionRepo
from app.domain.value_objects import Amount
from app.infrastructure.postgres.models import TransactionORM


class TransactionRepository(ITransactionRepo):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, transaction: Transaction) -> None:
        orm = await self.session.get(TransactionORM, transaction.id)

        if orm is None:
            orm = self._to_orm(transaction)
            self.session.add(orm)
        else:
            orm.status = transaction.status.value
            orm.cancelled_transaction_id = transaction.cancelled_transaction_id
            orm.updated_at = transaction.updated_at

    async def get_by_id(self, transaction_id: UUID) -> Transaction | None:
        orm = await self.session.get(TransactionORM, transaction_id)
        return self._to_entity(orm) if orm else None

    async def list_by_user(
        self,
        user_id: UUID,
        *,
        currency_id: UUID | None = None,
        status: TransactionStatus | None = None,
        transaction_type: TransactionType | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Transaction]:
        stmt = select(TransactionORM).where(TransactionORM.user_id == user_id)

        if currency_id is not None:
            stmt = stmt.where(TransactionORM.currency_id == currency_id)

        if status is not None:
            stmt = stmt.where(TransactionORM.status == status.value)

        if transaction_type is not None:
            stmt = stmt.where(TransactionORM.type == transaction_type.value)

        stmt = (
            stmt.order_by(TransactionORM.created_at.desc()).limit(limit).offset(offset)
        )

        result = await self.session.scalars(stmt)

        return [self._to_entity(orm) for orm in result.all()]

    def _to_entity(self, orm: TransactionORM) -> Transaction:
        return Transaction(
            id=orm.id,
            user_id=orm.user_id,
            currency_id=orm.currency_id,
            amount=Amount(orm.amount),
            type=(
                orm.type
                if isinstance(orm.type, TransactionType)
                else TransactionType(orm.type)
            ),
            status=(
                orm.status
                if isinstance(orm.status, TransactionStatus)
                else TransactionStatus(orm.status)
            ),
            cancelled_transaction_id=orm.cancelled_transaction_id,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    def _to_orm(self, transaction: Transaction) -> TransactionORM:
        return TransactionORM(
            id=transaction.id,
            user_id=transaction.user_id,
            currency_id=transaction.currency_id,
            amount=transaction.amount.value,
            type=transaction.type.value,
            status=transaction.status.value,
            cancelled_transaction_id=transaction.cancelled_transaction_id,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at,
        )
