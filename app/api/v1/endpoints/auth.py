from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, status

from app.api.v1.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.application.commands.login_user import LoginUserCommand
from app.application.commands.logout_user import LogoutUserCommand
from app.application.commands.refresh_token import RefreshTokenCommand
from app.application.commands.register_user import RegisterUserCommand
from app.application.services.token_service import TokenService
from app.core.dependencies import (
    AccessTokenDep,
    LoginHandlerDep,
    LogoutHandlerDep,
    RefreshHandlerDep,
    RegisterHandlerDep,
)
from app.domain.exceptions import InvalidTokenError

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    body: RegisterRequest,
    handler: RegisterHandlerDep,
    login_handler: LoginHandlerDep,
):
    await handler.execute(
        RegisterUserCommand(
            email=body.email,
            plain_password=body.password,
        )
    )
    tokens = await login_handler.execute(
        LoginUserCommand(email=body.email, password=body.password)
    )
    return TokenResponse(
        access_token=tokens.access_token, refresh_token=tokens.refresh_token
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, handler: LoginHandlerDep):
    tokens = await handler.execute(
        LoginUserCommand(email=body.email, password=body.password)
    )
    return TokenResponse(
        access_token=tokens.access_token, refresh_token=tokens.refresh_token
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, handler: RefreshHandlerDep):
    tokens = await handler.execute(
        RefreshTokenCommand(refresh_token=body.refresh_token)
    )
    return TokenResponse(
        access_token=tokens.access_token, refresh_token=tokens.refresh_token
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    access_token: AccessTokenDep,
    handler: LogoutHandlerDep,
):
    try:
        payload = TokenService().decode_token(access_token)
        await handler.execute(
            LogoutUserCommand(
                access_token=access_token,
                user_id=UUID(payload["sub"]),
            )
        )
    except InvalidTokenError:
        pass
