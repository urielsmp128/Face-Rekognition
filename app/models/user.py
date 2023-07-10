from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, root_validator, EmailStr, Field


class User(BaseModel):
    id: str = str(uuid.uuid1())
    name: str
    last_name: Optional[str]
    username: Optional[str]
    email: str
    password: str
    status: int = 1
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    @root_validator
    def number_validator(cls, values):
        values["updated_at"] = datetime.now()
        return values


class AuthUser(BaseModel):
    name: str = Field(..., description="User's name")
    last_name: str = Field(..., description="User's last name")
    email: EmailStr = Field(..., description="user email")
    password: str = Field(
        ..., min_length=8, max_length=20, description="user password"
    )


class SignInUser(BaseModel):
    email: EmailStr = Field(..., description="user email")
    password: str = Field(
        ..., min_length=8, max_length=20, description="user password"
    )


class UserSignUpResponse(BaseModel):
    id: Optional[str]
    name: str
    last_name: str
    username: str
    email: str
    created_at: datetime = datetime.now()


class UserImage(BaseModel):
    id: Optional[str]
    name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    email: Optional[str]


class RecoverPassword(BaseModel):
    email: EmailStr


class NewPassword(BaseModel):
    password: str = Field(
        ..., min_length=8, max_length=20, description="user new password"
    )
    confirm_password: str = Field(
        ..., min_length=8, max_length=20, description="user confirmed password"
    )
