from fastapi import APIRouter, status, Depends, Request

from app.models.user import (
    AuthUser,
    User,
    SignInUser,
    RecoverPassword,
    NewPassword,
)
from app.utils.errors_handler import responses
from app.utils.JWTBearer import JWTBearer
import app.services.user as Service
from app.utils.auth import AuthHandler

TAG = "User"
PREFIX = "/users"
tag_sign_up = "Sign Up"
prefix_sign_up = "/sign_up"
tag_sign_in = "Sign In"
prefix_sign_in = "/sign_in"
prefix_recover_password = "/recover_password"
tag_recover_password = "Recover Password"
prefix_reset_password = "/reset_password"
tag_reset_password = "Reset Password"

user = APIRouter()
authhandler = AuthHandler()

""""
Only route secure with login authentication
"""


@user.get(PREFIX + "/me", dependencies=[Depends(JWTBearer())], tags=[TAG])
async def find_user_by_token(request: Request):
    authorization = (request.headers.get("Authorization")).replace(
        "Bearer ", ""
    )
    email = authhandler.decode_token(authorization)
    resp = await Service.find_user_by_email(email)
    if resp is None:
        return responses[404]
    return resp


@user.get(PREFIX + "/{id}", dependencies=[Depends(JWTBearer())], tags=[TAG])
async def find_user_by_id(id: str):
    resp = await Service.find_user_by_id(id)
    if resp is None:
        return responses[404]
    return resp


@user.get(PREFIX, dependencies=[Depends(JWTBearer())], tags=[TAG])
async def find_users(page: int = 0, size: int = 10):
    return await Service.find_users(page, size)


@user.put(PREFIX + "/{id}", dependencies=[Depends(JWTBearer())], tags=[TAG])
async def update_user(id: str, user: User):
    resp = await Service.update_user(id, user)
    if resp is None:
        return responses[404]
    return resp


@user.delete(
    PREFIX + "/{id}",
    dependencies=[Depends(JWTBearer())],
    status_code=status.HTTP_204_NO_CONTENT,
    tags=[TAG],
)
async def delete_user(id: str):
    await Service.delete_user(id)
    return responses[204]


@user.post(prefix_sign_up, tags=[tag_sign_up])
async def sign_up(user: AuthUser):
    response = await Service.sign_up(user)
    if response is None:
        return responses[409]
    return response


@user.post(prefix_sign_in, tags=[tag_sign_in])
async def sign_in(user: SignInUser):
    response = await Service.sign_in(user)
    if response is None:
        return responses[401]
    return response


@user.post(prefix_recover_password + "/{token}", tags=[tag_recover_password])
async def recover_password(user: RecoverPassword):
    response = await Service.recover_password(user)
    if response is None:
        return responses[404]
    return response


@user.put(prefix_reset_password + "/{token}", tags=[tag_reset_password])
async def reset_password(token: str, newPassword: NewPassword):
    response = await Service.reset_password(token, newPassword)
    if response is None:
        return responses[401]
    return response
