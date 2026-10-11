from __future__ import annotations

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    ServiceError,
    TooManyAttemptsError,
    UserAlreadyExistsError,
)

logger = logging.getLogger(__name__)

_STATUS_MAP = {
    InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
    InvalidTokenError: status.HTTP_401_UNAUTHORIZED,
    UserAlreadyExistsError: status.HTTP_409_CONFLICT,
    TooManyAttemptsError: status.HTTP_429_TOO_MANY_REQUESTS,
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

    @app.exception_handler(ServiceError)
    async def _service_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled service error: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal Server Error"},
        )
