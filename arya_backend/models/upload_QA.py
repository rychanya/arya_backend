from bson import ObjectId
from pydantic import BaseModel, Field

from arya_backend.models.qa import StrObjectId


class Foreign(BaseModel):
    class Config:
        json_encoders = {ObjectId: lambda v: str(v)}

    id: StrObjectId
    col: str
    new: bool = False


class Upload(BaseModel):
    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: lambda v: str(v)}

    id: StrObjectId = Field(None, alias="_id")
    by: StrObjectId
    data: list[Foreign] = []

class Payload(BaseModel):
    __root__: dict[str, list[dict[str, str]]]  # type: ignore

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]