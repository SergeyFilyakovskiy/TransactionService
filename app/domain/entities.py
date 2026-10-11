from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from app.core.enums import ReportStatus, TransactionStatus, TransactionType
from app.domain.exceptions import (
    AccountFrozenError,
    InsufficientBalanceError,
    InvalidReportStatusError,
    InvalidTransactionStatusError,
)
from app.domain.value_objects import Amount, CurrencyCode, Email, HashedPassword

# ── User ──────────────────────────────────────────────────


@dataclass
class User:
    id: UUID
    email: Email
    hashed_password: HashedPassword
    is_frozen: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def change_email(self, new_email: str) -> None:
        object.__setattr__(self, "email", Email(new_email))

    def verify_password(self, plain: str) -> bool:
        if self.hashed_password is None:
            return False

        return self.hashed_password.verify(plain)

    def freeze(self) -> None:
        self.is_frozen = True
        self.updated_at = datetime.now(timezone.utc)

    def unfreeze(self) -> None:
        self.is_frozen = False
        self.updated_at = datetime.now(timezone.utc)

    def check_not_frozen(self) -> None:
        """Raise AccountFrozenError if account is frozen."""
        if self.is_frozen:
            raise AccountFrozenError(self.id)


# ── Currency ─────────────────────────────────────────────


@dataclass
class Currency:
    id: UUID
    code: CurrencyCode
    name: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(cls, code: str, name: str) -> "Currency":
        now = datetime.now(timezone.utc)

        return cls(
            id=uuid4(),
            code=CurrencyCode(code),
            name=name.strip(),
            created_at=now,
            updated_at=now,
        )

    def change_name(self, name: str) -> None:
        self.name = name.strip()
        self.updated_at = datetime.now(timezone.utc)


# ─ Balance ───────────────────────────────────────────────


@dataclass
class Balance:
    id: UUID
    user_id: UUID
    currency_id: UUID
    amount: Amount
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        user_id: UUID,
        currency_id: UUID,
        amount: Amount | Decimal | int | str = Decimal("0"),
    ) -> "Balance":
        now = datetime.now(timezone.utc)

        return cls(
            id=uuid4(),
            user_id=user_id,
            currency_id=currency_id,
            amount=cls._to_amount(amount),
            created_at=now,
            updated_at=now,
        )

    def credit(self, amount: Amount | Decimal | int | str) -> None:
        """Increase balance (for deposits and withdrawal cancellations)."""
        amount = self._to_amount(amount)

        if amount.value <= 0:
            raise ValueError("Credit amount must be positive")

        self.amount = self.amount.add(amount)
        self.updated_at = datetime.now(timezone.utc)

    def debit(self, amount: Amount | Decimal | int | str) -> None:
        """Decrease balance (for withdrawals and deposit cancellations)."""
        amount = self._to_amount(amount)

        if amount.value <= 0:
            raise ValueError("Debit amount must be positive")

        if self.amount.value < amount.value:
            raise InsufficientBalanceError(self.amount.value, amount.value)

        self.amount = self.amount.subtract(amount)
        self.updated_at = datetime.now(timezone.utc)

    def has_funds(self, amount: Amount | Decimal | int | str) -> bool:
        amount = self._to_amount(amount)
        return self.amount.value >= amount.value

    @staticmethod
    def _to_amount(value: Amount | Decimal | int | str) -> Amount:
        if isinstance(value, Amount):
            return value

        return Amount(value)  # pyright: ignore[reportArgumentType]


# ── Transaction ───────────────────────────────────────────


@dataclass
class Transaction:
    id: UUID
    user_id: UUID
    currency_id: UUID
    amount: Amount
    type: TransactionType
    status: TransactionStatus = TransactionStatus.PENDING
    cancelled_transaction_id: UUID | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        user_id: UUID,
        currency_id: UUID,
        amount: Amount | Decimal | int | str,
        transaction_type: TransactionType | str,
    ) -> "Transaction":
        if isinstance(transaction_type, str):
            transaction_type = TransactionType(transaction_type)

        amount = cls._to_amount(amount)

        if amount.value <= 0:
            raise ValueError("Transaction amount must be positive")

        now = datetime.now(timezone.utc)

        return cls(
            id=uuid4(),
            user_id=user_id,
            currency_id=currency_id,
            amount=amount,
            type=transaction_type,
            status=TransactionStatus.PENDING,
            cancelled_transaction_id=None,
            created_at=now,
            updated_at=now,
        )

    def mark_completed(self) -> None:
        self._ensure_in_status(TransactionStatus.PENDING)

        self.status = TransactionStatus.COMPLETED
        self.updated_at = datetime.now(timezone.utc)

    def mark_failed(self) -> None:
        self._ensure_in_status(TransactionStatus.PENDING)

        self.status = TransactionStatus.FAILED
        self.updated_at = datetime.now(timezone.utc)

    def mark_cancelled(
        self,
        cancelled_by_transaction_id: UUID | None = None,
    ) -> None:
        """
        Mark transaction as cancelled.
        """
        self._ensure_in_status(TransactionStatus.PENDING, TransactionStatus.COMPLETED)

        self.status = TransactionStatus.CANCELLED
        self.cancelled_transaction_id = cancelled_by_transaction_id
        self.updated_at = datetime.now(timezone.utc)

    def set_cancellation_reference(self, transaction_id: UUID) -> None:
        self.cancelled_transaction_id = transaction_id
        self.updated_at = datetime.now(timezone.utc)

    @property
    def is_deposit(self) -> bool:
        return self.type == TransactionType.DEPOSIT

    @property
    def is_withdrawal(self) -> bool:
        return self.type == TransactionType.WITHDRAWAL

    @property
    def is_cancelled(self) -> bool:
        return self.status == TransactionStatus.CANCELLED

    def _ensure_in_status(self, *allowed_statuses: TransactionStatus) -> None:
        if self.status not in allowed_statuses:
            raise InvalidTransactionStatusError(
                f"Transaction {self.id} has invalid status: {self.status}. "
                f"Allowed: {', '.join(s.value for s in allowed_statuses)}"
            )

    @staticmethod
    def _to_amount(value: Amount | Decimal | int | str) -> Amount:
        if isinstance(value, Amount):
            return value

        return Amount(value)  # pyright: ignore[reportArgumentType]


# ── ReportFile ────────────────────────────────────────────


@dataclass
class ReportFile:
    id: UUID
    user_id: UUID
    status: ReportStatus = ReportStatus.PENDING
    url: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(cls, user_id: UUID) -> "ReportFile":
        now = datetime.now(timezone.utc)

        return cls(
            id=uuid4(),
            user_id=user_id,
            status=ReportStatus.PENDING,
            url=None,
            created_at=now,
            updated_at=now,
        )

    def mark_processing(self) -> None:
        self._ensure_in_status(ReportStatus.PENDING)

        self.status = ReportStatus.PROCESSING
        self.updated_at = datetime.now(timezone.utc)

    def mark_completed(self, url: str) -> None:
        self._ensure_in_status(ReportStatus.PENDING, ReportStatus.PROCESSING)

        if not url:
            raise ValueError("Report file URL is required")

        self.url = url
        self.status = ReportStatus.COMPLETED
        self.updated_at = datetime.now(timezone.utc)

    def mark_failed(self) -> None:
        self._ensure_in_status(ReportStatus.PENDING, ReportStatus.PROCESSING)

        self.status = ReportStatus.FAILED
        self.updated_at = datetime.now(timezone.utc)

    def _ensure_in_status(self, *allowed_statuses: ReportStatus) -> None:
        if self.status not in allowed_statuses:
            raise InvalidReportStatusError(
                f"Report file {self.id} has invalid status: {self.status}. "
                f"Allowed: {', '.join(s.value for s in allowed_statuses)}"
            )
