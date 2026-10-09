class ServiceError(Exception):
    """Service base exception"""


class UserAlreadyExistsError(ServiceError):
    def __init__(self, email: str):
        super().__init__(f"User with email '{email}' already exists")


class UserNotFoundError(ServiceError):
    pass


class UserInactiveError(ServiceError):
    pass


class InvalidCredentialsError(ServiceError):
    pass


class TooManyAttemptsError(ServiceError):
    pass


class InvalidTokenError(ServiceError):
    pass
