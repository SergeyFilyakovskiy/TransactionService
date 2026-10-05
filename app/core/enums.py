from enum import StrEnum


class TransactionStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TransactionType(StrEnum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"


class ReportStatus(StrEnum):

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
