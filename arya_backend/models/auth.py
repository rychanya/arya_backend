from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
    scopes: list[str] = []


class User(BaseModel):
    username: str
    disabled: Optional[bool] = False


class SignInUser(BaseModel):
    username: str
    password: str


class UserInDB(User):
    hashed_password: str
    scopes: list[str] = []
