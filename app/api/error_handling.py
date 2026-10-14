from __future__ import annotations

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    AccountFrozenError,
    BalanceAlreadyExistsError,
    BalanceNotFoundError,
    CurrencyAlreadyExistsError,
    CurrencyNotFoundError,
    DomainError,
    InsufficientBalanceError,
    InvalidCredentialsError,
    InvalidReportStatusError,
    InvalidTokenError,
    InvalidTransactionStatusError,
    ReportFileNotFoundError,
    ServiceError,
    TooManyAttemptsError,
    TransactionAlreadyCancelledError,
    TransactionNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
)

logger = logging.getLogger(__name__)

_STATUS_MAP = {
    # Auth
    InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
    InvalidTokenError: status.HTTP_401_UNAUTHORIZED,
    TooManyAttemptsError: status.HTTP_429_TOO_MANY_REQUESTS,
    # User
    UserAlreadyExistsError: status.HTTP_409_CONFLICT,
    UserNotFoundError: status.HTTP_404_NOT_FOUND,
    AccountFrozenError: status.HTTP_403_FORBIDDEN,
    # Currency
    CurrencyAlreadyExistsError: status.HTTP_409_CONFLICT,
    CurrencyNotFoundError: status.HTTP_404_NOT_FOUND,
    # Balance
    BalanceNotFoundError: status.HTTP_404_NOT_FOUND,
    BalanceAlreadyExistsError: status.HTTP_409_CONFLICT,
    InsufficientBalanceError: status.HTTP_400_BAD_REQUEST,
    # Transaction
    TransactionNotFoundError: status.HTTP_404_NOT_FOUND,
    InvalidTransactionStatusError: status.HTTP_400_BAD_REQUEST,
    TransactionAlreadyCancelledError: status.HTTP_409_CONFLICT,
    # Report
    ReportFileNotFoundError: status.HTTP_404_NOT_FOUND,
    InvalidReportStatusError: status.HTTP_400_BAD_REQUEST,
}


def _make_handler(status_code: int):
    async def handler(request: Request, exc: Exception) -> JSONResponse:
        headers = None
        retry_after = getattr(exc, "retry_after", None)
        if retry_after is not None:
            headers = {"Retry-After": str(retry_after)}
        return JSONResponse(
            status_code=status_code,
            content={"detail": str(exc)},
            headers=headers,
        )

    return handler


def register_exception_handlers(app: FastAPI) -> None:
    for exc_cls, status_code in _STATUS_MAP.items():
        app.add_exception_handler(exc_cls, _make_handler(status_code))

    @app.exception_handler(DomainError)
    async def _domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        logger.exception("Unhandled domain error: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ServiceError)
    async def _service_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled service error: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal Server Error"},
        )
