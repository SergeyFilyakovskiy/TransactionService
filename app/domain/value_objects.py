from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import ROUND_DOWN, Decimal, InvalidOperation

import bcrypt

AMOUNT_QUANTUM = Decimal("0.00000001")


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not isinstance(self.value, str):
            raise TypeError("Email must be a string")

        normalized = self.value.strip().lower()

        if not re.match(r"^[\w.+-]+@[\w-]+\.[a-z]{2,}$", normalized):
            raise ValueError(f"Invalid email format: {self.value}")

        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class HashedPassword:
    value: str

    @staticmethod
    def from_plain(plain: str) -> "HashedPassword":
        if len(plain) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(plain) > 128:
            raise ValueError("Password is too long")

        hashed = bcrypt.hashpw(plain.encode(), bcrypt.gensalt())
        return HashedPassword(hashed.decode())

    @staticmethod
    def from_hash(hashed: str) -> "HashedPassword":
        return HashedPassword(hashed)

    def verify(self, plain: str) -> bool:
        return bcrypt.checkpw(plain.encode(), self.value.encode())

    def __repr__(self) -> str:
        return "HashedPassword(value=***)"


@dataclass(frozen=True)
class CurrencyCode:
    value: str

    def __post_init__(self):
        if not isinstance(self.value, str):
            raise TypeError("Currency code must be a string")

        normalized = self.value.strip().upper()

        if not re.match(r"^[A-Z0-9]{2,10}$", normalized):
            raise ValueError(f"Invalid currency code: {self.value}")

        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Amount:
    value: Decimal

    def __post_init__(self):
        if isinstance(self.value, bool):
            raise TypeError("Amount cannot be bool")

        try:
            raw_value = self.value
            if isinstance(raw_value, Decimal):
                decimal_value = raw_value
            else:
                decimal_value = Decimal(str(raw_value))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ValueError("Invalid decimal amount") from exc

        if not decimal_value.is_finite():
            raise ValueError("Amount must be finite")

        if decimal_value < 0:
            raise ValueError("Amount cannot be negative")

        decimal_value = decimal_value.quantize(
            AMOUNT_QUANTUM,
            rounding=ROUND_DOWN,
        )

        object.__setattr__(self, "value", decimal_value)

    @classmethod
    def zero(cls) -> "Amount":
        return cls(Decimal("0"))

    def add(self, other: "Amount") -> "Amount":
        return Amount(self.value + other.value)

    def subtract(self, other: "Amount") -> "Amount":
        if self.value < other.value:
            raise ValueError("Amount cannot be negative")

        return Amount(self.value - other.value)

    def is_zero(self) -> bool:
        return self.value == Decimal("0")

    def __str__(self) -> str:
        return str(self.value)
