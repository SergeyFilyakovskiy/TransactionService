import uuid
from decimal import Decimal

from sqlalchemy import UUID, Boolean, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import Base
from app.core.enums import ReportStatus, TransactionStatus


class CurrencyORM(Base):
    __tablename__ = "currencies"

    code: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        nullable=False,
        comment="Code (USD, EUR, BTC)",
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Full name",
    )

    balances: Mapped[list["BalanceORM"]] = relationship(
        back_populates="currency",
        cascade="all, delete-orphan",
    )

    transactions: Mapped[list["TransactionORM"]] = relationship(
        back_populates="currency",
        cascade="all, delete-orphan",
    )


class UserORM(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    is_frozen: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    balances: Mapped[list["BalanceORM"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    transactions: Mapped[list["TransactionORM"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    reports: Mapped[list["ReportFilesORM"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class BalanceORM(Base):
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

    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=8),
        default=Decimal("0"),
        nullable=False,
    )

    user: Mapped["UserORM"] = relationship(
        back_populates="balances",
    )

    currency: Mapped["CurrencyORM"] = relationship(
        back_populates="balances",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "currency_id",
            name="uq_user_currency",
        ),
    )


class TransactionORM(Base):
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

    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=8),
        nullable=False,
        comment="Transaction amount",
    )

    type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Type: deposit or withdrawal",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default=TransactionStatus.PENDING.value,
        nullable=False,
    )

    cancelled_transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID,
        ForeignKey("transactions.id"),
        nullable=True,
        comment="Related transaction ID for cancellation",
    )

    user: Mapped["UserORM"] = relationship(
        back_populates="transactions",
    )

    currency: Mapped["CurrencyORM"] = relationship(
        back_populates="transactions",
    )

    cancelled_transaction: Mapped["TransactionORM | None"] = relationship(
        "TransactionORM",
        remote_side="TransactionORM.id",
        foreign_keys=[cancelled_transaction_id],
        uselist=False,
    )


class ReportFilesORM(Base):
    __tablename__ = "report_files"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("users.id"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=ReportStatus.PENDING.value,
    )

    url: Mapped[str | None] = mapped_column(
        String,
        unique=True,
        nullable=True,
    )

    user: Mapped["UserORM"] = relationship(
        back_populates="reports",
    )
