from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.v1.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.application.commands.login_user import LoginUserCommand, LoginUserHandler
from app.application.commands.logout_user import LogoutUserCommand, LogoutUserHandler
from app.application.commands.refresh_token import (
    RefreshTokenCommand,
    RefreshTokenHandler,
)
from app.application.commands.register_user import (
    RegisterUserCommand,
    RegisterUserHandler,
)
from app.application.services.token_service import TokenService
from app.core.dependencies import (
    get_access_token,
    get_login_handler,
    get_logout_handler,
    get_refresh_handler,
    get_register_handler,
)
from app.domain.exceptions import InvalidTokenError

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    body: RegisterRequest,
    handler: RegisterUserHandler = Depends(get_register_handler),
    login_handler: LoginUserHandler = Depends(get_login_handler),
):
    await handler.handle(
        RegisterUserCommand(
            email=body.email,
            password=body.password,
        )
    )
    tokens = await login_handler.handle(
        LoginUserCommand(email=body.email, password=body.password)
    )
    return TokenResponse(
        access_token=tokens.access_token, refresh_token=tokens.refresh_token
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest, handler: LoginUserHandler = Depends(get_login_handler)
):
    tokens = await handler.handle(
        LoginUserCommand(email=body.email, password=body.password)
    )
    return TokenResponse(
        access_token=tokens.access_token, refresh_token=tokens.refresh_token
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest, handler: RefreshTokenHandler = Depends(get_refresh_handler)
):
    tokens = await handler.handle(RefreshTokenCommand(refresh_token=body.refresh_token))
    return TokenResponse(
        access_token=tokens.access_token, refresh_token=tokens.refresh_token
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    access_token: str = Depends(get_access_token),
    handler: LogoutUserHandler = Depends(get_logout_handler),
):
    try:
        payload = TokenService().decode_token(access_token)
        await handler.handle(
            LogoutUserCommand(
                access_token=access_token,
                user_id=UUID(payload["sub"]),
            )
        )
    except InvalidTokenError:
        pass
