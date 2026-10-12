class AppError(Exception):
    """Base application exception."""


class ServiceError(AppError):
    """Unexpected internal error -> HTTP 500."""


class DomainError(AppError):
    """Business-rule violation -> HTTP 4xx (mapping lives in presentation layer)."""


# ── User ──────────────────────────────────────────────────


class UserAlreadyExistsError(DomainError):
    def __init__(self, email: str):
        super().__init__(f"User with email '{email}' already exists")


class UserNotFoundError(DomainError):
    def __init__(self, message: str = "User not found"):
        super().__init__(message)


class InvalidCredentialsError(DomainError):
    pass


class TooManyAttemptsError(DomainError):
    def __init__(self, retry_after: int | None = None):
        super().__init__("Too many failed attempts, try again later")
        self.retry_after = retry_after


class InvalidTokenError(DomainError):
    pass


class AccountFrozenError(DomainError):
    def __init__(self, user_id):
        super().__init__(f"Account {user_id} is frozen. All operations are blocked.")


# ── Currency ──────────────────────────────────────────────


class CurrencyAlreadyExistsError(DomainError):
    def __init__(self, code: str):
        super().__init__(f"Currency with code '{code}' already exists")


class CurrencyNotFoundError(DomainError):
    def __init__(self, message: str = "Currency not found"):
        super().__init__(message)


# ── Balance ──────────────────────────────────────────────


class BalanceNotFoundError(DomainError):
    def __init__(self, message: str = "Balance not found"):
        super().__init__(message)


class BalanceAlreadyExistsError(DomainError):
    def __init__(self, user_id, currency_id):
        super().__init__(
            f"Balance already exists for user_id={user_id}, currency_id={currency_id}"
        )


class InsufficientBalanceError(DomainError):
    def __init__(self, current, requested):
        super().__init__(
            f"Insufficient balance: current={current}, requested={requested}"
        )


# ── Transaction ───────────────────────────────────────────


class TransactionNotFoundError(DomainError):
    def __init__(self, message: str = "Transaction not found"):
        super().__init__(message)


class InvalidTransactionStatusError(DomainError):
    pass


class TransactionAlreadyCancelledError(DomainError):
    pass


# ── Report ────────────────────────────────────────────────


class ReportFileNotFoundError(DomainError):
    def __init__(self, message: str = "Report file not found"):
        super().__init__(message)


class InvalidReportStatusError(DomainError):
    pass
