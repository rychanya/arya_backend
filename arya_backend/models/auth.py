from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from arya_backend.models.qa import StrObjectId


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
    scopes: list[str] = []


class User(BaseModel):
    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: lambda v: str(v)}

    id: StrObjectId = Field(None, alias="_id")
    username: str
    disabled: Optional[bool] = False


class SignInUser(BaseModel):
    username: str
    password: str


class UserInDB(User):
    hashed_password: str
    scopes: list[str] = []
