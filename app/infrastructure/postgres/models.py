import uuid

from sqlalchemy import UUID, Boolean, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import Base
from app.core.enums import ReportStatus, TransactionStatus, TransactionType


class Currency(Base):
    __tablename__ = "currencies"

    code: Mapped[str] = mapped_column(
        String(10), unique=True, nullable=False, comment="Code (USD, EUR, BTC)"
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Full name")

    balances: Mapped[list["Balance"]] = relationship(back_populates="currency")


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    is_frozen: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    balances: Mapped[list["Balance"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    reports: Mapped[uuid.UUID] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Balance(Base):
    __tablename__ = "balances"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("users.id"),
        nullable=False,
    )

    currency_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("currencies.id"),
        nullable=False,
    )

    amount: Mapped[Numeric] = mapped_column(
        Numeric(precision=20, scale=8),
        default=0,
        nullable=False,
        comment="Текущий баланс",
    )

    user: Mapped["User"] = relationship(back_populates="balances")

    currency: Mapped["Currency"] = relationship(back_populates="balances")

    __table_args__ = (
        UniqueConstraint("user_id", "currency_id", name="uq_user_currency"),
    )


class Transaction(Base):
    __tablename__ = "transactions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("users.id"),
        nullable=False,
    )

    currency_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("currencies.id"),
        nullable=False,
    )

    amount: Mapped[Numeric] = mapped_column(
        Numeric(precision=20, scale=8), nullable=False, comment="Transaction amount"
    )

    type: Mapped[TransactionType] = mapped_column(
        String(20), nullable=False, comment="Type: deposit or withdrawal"
    )

    status: Mapped[TransactionStatus] = mapped_column(
        String(20),
        default=TransactionStatus.PENDING,
        nullable=False,
    )

    cancelled_transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID,
        ForeignKey("transactions.id"),
        nullable=True,
        comment="Transaction ID for cancel",
    )

    user: Mapped["User"] = relationship(back_populates="transactions")

    currency: Mapped["Currency"] = relationship()

    cancelled_transaction: Mapped["Transaction | None"] = relationship(
        remote_side="Transaction.id", foreign_keys=[cancelled_transaction_id]
    )


class ReportFiles(Base):
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("users.id"),
        nullable=False,
    )

    status: Mapped[ReportStatus] = mapped_column(
        String(20),
        nullable=False,
        default=ReportStatus.PENDING,
    )

    url: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=True,
    )

    user: Mapped["User"] = relationship(back_populates="reports")
