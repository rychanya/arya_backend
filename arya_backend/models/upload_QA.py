from bson import ObjectId
from pydantic import BaseModel, Field, validator

from arya_backend.models.qa import QA, StrObjectId


class Payload(BaseModel):
    class Config:
        json_encoders = {ObjectId: lambda v: str(v)}

    type: QA.type_enum
    answer: str
    title: str
    question: str
    is_correct: bool
    foreign_id: StrObjectId = Field(None)

    @validator("type", pre=True)
    def check_type(cls, v: str):
        if type == "единственный выбор":
            return QA.type_enum.one.value
        elif type == "множественный выбор":
            return QA.type_enum.many.value
        else:
            raise ValueError("incorrect type")

    @validator("answer")
    def parse_answer(cls, v: str, values):
        _type = values.get("type")
        if _type is None:
            raise ValueError
        if _type == QA.type_enum.one:
            return v
        elif _type == QA.type_enum.many:
            return v.split(";\r\r\n")
        else:
            raise ValueError

    @validator("title")
    def normalize_title(cls, v: str):
        try:
            return v.encode("cp1251").decode("utf8")
        except UnicodeDecodeError:
            return v

    @validator("is_correct", pre=True)
    def check_is_correct(cls, v: str):
        if v == "+":
            return True
        elif v == "-":
            return False
        else:
            raise ValueError("incorrect is_correct")


class Upload(BaseModel):
    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: lambda v: str(v)}

    id: StrObjectId = Field(None, alias="_id")
    by: StrObjectId
    data: list[Payload] = []
