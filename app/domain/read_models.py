from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class WeeklyReportRow:
    week_start: date
    week_end: date
    new_users_count: int
    users_with_deposit_count: int
    deposits_sum: Decimal
    withdrawals_sum: Decimal
    total_transactions_count: int
    transactions_without_cancels_count: int
