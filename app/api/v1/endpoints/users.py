from uuid import UUID

from fastapi import APIRouter

from app.api.v1.schemas.user import FreezeUserRequest, UnfreezeUserRequest, UserResponse
from app.application.commands.freeze_user import FreezeUserCommand
from app.application.commands.unfreeze_user import UnfreezeUserCommand
from app.application.queries.get_user import GetUserQuery
from app.core.dependencies import (
    AccessTokenDep,
    FreezeUserHandlerDep,
    GetUserHandlerDep,
    TokenServiceDep,
    UnfreezeUserHandlerDep,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/freeze", response_model=UserResponse)
async def freeze_user(
    body: FreezeUserRequest,
    handler: FreezeUserHandlerDep,
):
    user = await handler.execute(FreezeUserCommand(user_id=body.user_id))
    return user


@router.post("/unfreeze", response_model=UserResponse)
async def unfreeze_user(
    body: UnfreezeUserRequest,
    handler: UnfreezeUserHandlerDep,
):
    user = await handler.execute(UnfreezeUserCommand(user_id=body.user_id))
    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    access_token: AccessTokenDep,
    handler: GetUserHandlerDep,
    token_service: TokenServiceDep,
):
    payload = token_service.decode_token(access_token)
    user = await handler.execute(GetUserQuery(user_id=UUID(payload["sub"])))
    return user
