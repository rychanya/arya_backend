from bson import ObjectId
from pydantic import BaseModel, Field

from arya_backend.models.qa import StrObjectId


class Payload(BaseModel):
    class Config:
        json_encoders = {ObjectId: lambda v: str(v)}

    answer: str
    title: str
    question: str
    type: str
    is_correct: str
    foreign_id: StrObjectId = Field(None)


class Upload(BaseModel):
    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: lambda v: str(v)}

    id: StrObjectId = Field(None, alias="_id")
    by: StrObjectId
    data: list[Payload] = []
