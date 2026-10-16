from __future__ import annotations

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import TransactionStatus, TransactionType
from app.domain.interfaces.i_report_query_repo import IReportQueryRepo
from app.domain.read_models import WeeklyReportRow
from app.infrastructure.postgres.models import TransactionORM, UserORM


class ReportQueryRepository(IReportQueryRepo):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_weekly_report(self, weeks: int = 52) -> list[WeeklyReportRow]:
        first_monday = self._first_monday(weeks)
        since = datetime.combine(first_monday, time.min, tzinfo=None)

        tx_rows = await self._transactions_agg(since)
        user_rows = await self._new_users_agg(since)

        result: list[WeeklyReportRow] = []
        for i in range(weeks):
            week_start = first_monday + timedelta(weeks=i)
            tx = tx_rows.get(week_start)
            result.append(
                WeeklyReportRow(
                    week_start=week_start,
                    week_end=week_start + timedelta(days=6),
                    new_users_count=user_rows.get(week_start, 0),
                    users_with_deposit_count=tx[0] if tx else 0,
                    deposits_sum=tx[1] if tx else Decimal("0"),
                    withdrawals_sum=tx[2] if tx else Decimal("0"),
                    total_transactions_count=tx[3] if tx else 0,
                    transactions_without_cancels_count=tx[4] if tx else 0,
                )
            )
        return result

    # ── queries ───────────────────────────────────────────

    async def _transactions_agg(self, since: datetime) -> dict[date, tuple]:
        week = func.date_trunc("week", TransactionORM.created_at)

        not_reversal = TransactionORM.cancelled_transaction_id.is_(None)
        is_cancelled = TransactionORM.status == TransactionStatus.CANCELLED.value
        is_deposit = TransactionORM.type == TransactionType.DEPOSIT.value
        is_withdrawal = TransactionORM.type == TransactionType.WITHDRAWAL.value

        stmt = (
            select(
                week.label("week_start"),
                func.count(func.distinct(TransactionORM.user_id))
                .filter(is_deposit & (not_reversal | is_cancelled))
                .label("users_with_deposit"),
                func.coalesce(
                    func.sum(TransactionORM.amount).filter(is_deposit & not_reversal),
                    0,
                ).label("deposits_sum"),
                func.coalesce(
                    func.sum(TransactionORM.amount).filter(
                        is_withdrawal & not_reversal
                    ),
                    0,
                ).label("withdrawals_sum"),
                func.count(TransactionORM.id)
                .filter(not_reversal | is_cancelled)
                .label("total_tx"),
                func.count(TransactionORM.id)
                .filter(not_reversal)
                .label("tx_without_cancels"),
            )
            .where(TransactionORM.created_at >= since)
            .group_by(week)
        )

        rows = (await self.session.execute(stmt)).all()
        return {
            self._as_date(r.week_start): (
                r.users_with_deposit,
                Decimal(str(r.deposits_sum)),
                Decimal(str(r.withdrawals_sum)),
                r.total_tx,
                r.tx_without_cancels,
            )
            for r in rows
        }

    async def _new_users_agg(self, since: datetime) -> dict[date, int]:
        week = func.date_trunc("week", UserORM.created_at)

        stmt = (
            select(
                week.label("week_start"),
                func.count(UserORM.id).label("new_users"),
            )
            .where(UserORM.created_at >= since)
            .group_by(week)
        )

        rows = (await self.session.execute(stmt)).all()
        return {self._as_date(r.week_start): r.new_users for r in rows}

    # ── helpers ───────────────────────────────────────────

    @staticmethod
    def _first_monday(weeks: int) -> date:
        today = date.today()
        current_monday = today - timedelta(days=today.weekday())
        return current_monday - timedelta(weeks=weeks - 1)

    @staticmethod
    def _as_date(value: Any) -> date:
        return value.date() if isinstance(value, datetime) else value
