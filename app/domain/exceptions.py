class AppError(Exception):
    """Base application exception."""


class ServiceError(AppError):
    """Unexpected internal error -> HTTP 500."""


class DomainError(AppError):
    """Business-rule violation -> HTTP 4xx (mapping lives in presentation layer)."""


class UserAlreadyExistsError(DomainError):
    def __init__(self, email: str):
        super().__init__(f"User with email '{email}' already exists")


class InvalidCredentialsError(DomainError):
    pass


class TooManyAttemptsError(DomainError):
    def __init__(self, retry_after: int | None = None):
        super().__init__("Too many failed attempts, try again later")
        self.retry_after = retry_after


class InvalidTokenError(DomainError):
    pass
