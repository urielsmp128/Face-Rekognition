from bson import ObjectId

from re import sub
from app.utils.security import Secure
from app.utils.auth import AuthHandler
from app.utils.JWTBearer import JWTBearer

from app.models.user import (
    AuthUser,
    User,
    SignInUser,
    RecoverPassword,
    NewPassword,
)
from app.config.db import conn
from app.schemas.user import userEntity, usersEntity
from app.utils.config import settings
from app.utils.send_email import send_recover_email

secure = Secure()
authhandler = AuthHandler()
jwtbearer = JWTBearer()

COLLECTION = (conn[settings.DATABASE_NAME]).user


async def find_user_by_id(id: str) -> dict:
    return userEntity(COLLECTION.find_one({"_id": ObjectId(id)}))


async def find_users(page: int = 0, size: int = 10) -> list:
    if page <= 0:
        return usersEntity(COLLECTION.find().limit(size))
    skip = page * size
    return usersEntity(COLLECTION.find().skip(skip).limit(size))


async def update_user(id: str, user: User) -> dict:
    userName = ""
    if user.last_name != "":
        userName = snake_case(user.name + " " + user.last_name)
    else:
        userName = snake_case(user.name)
    user.username = userName
    COLLECTION.find_one_and_update({"_id": ObjectId(id)}, {"$set": dict(user)})
    return userEntity(COLLECTION.find_one({"_id": ObjectId(id)}))


async def delete_user(id: str):
    COLLECTION.find_one_and_delete({"_id": ObjectId(id)})


def snake_case(s):
    return "_".join(
        sub(
            "([A-Z][a-z]+)",
            r" \1",
            sub("([A-Z]+)", r" \1", s.replace("-", " ")),
        ).split()
    ).lower()


async def sign_up(user: AuthUser) -> (dict | None):
    user1 = COLLECTION.find_one({"email": user.email})
    if user1:
        return None
    userName = ""
    if user.last_name != "":
        userName = snake_case(user.name + " " + user.last_name)
    else:
        userName = snake_case(user.name)

    sign_up_user = User(
        name=user.name,
        last_name=user.last_name,
        username=userName,
        email=user.email,
        password=secure.get_password(user.password),
    )
    COLLECTION.insert_one(dict(sign_up_user))
    return sign_up_user


async def sign_in(user: SignInUser) -> (dict | None):
    user_found = None
    user1 = COLLECTION.find_one({"email": user.email})
    if user1:
        password = user1["password"]
    user_found = user1
    if user_found is None or not secure.verify_password(
        user.password, password
    ):
        return None
    var1 = user_found["email"]
    token = authhandler.encode_token(var1)
    return {"token": token}


async def recover_password(user: RecoverPassword) -> (dict | None):
    user1 = COLLECTION.find_one({"email": user.email})
    if user1 is not None:
        reset_token = authhandler.encode_token(user1["id"])
        reset_link = f"http://localhost:8000/reset?token={reset_token}"
        send_recover_email.send_email(user1["email"], reset_link)
        return reset_token
    return None


async def reset_password(
    token: str, newPassword: NewPassword
) -> (dict | None):
    if authhandler.decode_token(token):
        new_password = newPassword.password
        if new_password == newPassword.confirm_password:
            user_id = authhandler.decode_token(token)
            user = COLLECTION.find_one({"id": user_id})
            COLLECTION.find_one_and_update(
                {"email": user["email"]},
                {"$set": {"password": secure.get_password(new_password)}},
            )
            return {"message": "Password updated correctly!"}
        return {"message": "Passwords doesn't match"}
    return None


async def find_user_by_email(email: str) -> dict:
    return userEntity(COLLECTION.find_one({"email": email}))
