from enum import Enum
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from bson import ObjectId
from pydantic import BaseModel, Field, constr
from pydantic.generics import GenericModel


class StrObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, str):
            if not ObjectId.is_valid(v):
                raise ValueError(f"{v} is not valid ObjectId")
            return ObjectId(v)
        elif isinstance(v, ObjectId):
            if not ObjectId.is_valid(str(v)):
                ValueError(f"{v} is not valid ObjectId")
            return v
        else:
            raise TypeError("str or ObjectId required")


class OneAnswer(BaseModel):
    __root__: constr(min_length=1)  # type: ignore


class ManyAnswer(BaseModel):
    __root__: List[constr(min_length=1)]  # type: ignore

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]


class JoinAnswer(BaseModel):
    __root__: Dict[constr(min_length=1), constr(min_length=1)]  # type: ignore

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]


AnswerType = TypeVar("AnswerType", OneAnswer, ManyAnswer, JoinAnswer)
Model = TypeVar("Model", bound="BaseModel")


class QA(GenericModel, Generic[AnswerType]):
    class type_enum(str, Enum):
        one = "Выберите один правильный вариант"
        many = "Выберите все правильные варианты"
        drag = "Перетащите варианты так, чтобы они оказались в правильном порядке"
        join = "Соедините соответствия справа с правильными вариантами"

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: lambda v: str(v)}
        allow_mutation = False

    id: StrObjectId = Field(None, alias="_id")
    type: type_enum
    question: constr(min_length=1)  # type: ignore
    answers: list[constr(min_length=1)]  # type: ignore
    extra_answers: list[str] = []
    correct: Optional[AnswerType]
    incorrect: List[AnswerType] = []
    tags: Dict[str, str] = {}

    @classmethod
    def parse_obj(cls: Type["Model"], obj: Any) -> "Model":
        if obj["type"] == cls.type_enum.one:  # type: ignore
            return cls[str]._parse_obj(obj)  # type: ignore
        if (obj["type"] == cls.type_enum.many) or (obj["type"] == cls.type_enum.drag):  # type: ignore
            return cls[list]._parse_obj(obj)  # type: ignore
        if obj["type"] == cls.type_enum.join:  # type: ignore
            return cls[dict]._parse_obj(obj)  # type: ignore
        else:
            return cls._parse_obj(obj)  # type: ignore

    @classmethod
    def _parse_obj(cls: Type["Model"], obj: Any) -> "Model":
        return super().parse_obj(obj)  # type: ignore


class QAIncomplete(GenericModel, Generic[AnswerType]):
    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: lambda v: str(v)}
        allow_mutation = False

    id: StrObjectId = Field(None, alias="_id")
    type: QA.type_enum
    question: constr(min_length=1)  # type: ignore
    answer: list[constr(min_length=1)]  # type: ignore
    title: str
    is_correct: bool
    by: list[StrObjectId]
    create: StrObjectId

    @classmethod
    def parse_obj(cls: Type["Model"], obj: Any) -> "Model":
        if obj["type"] == QA.type_enum.one:  # type: ignore
            return cls[str]._parse_obj(obj)  # type: ignore
        if (obj["type"] == QA.type_enum.many) or (obj["type"] == QA.type_enum.drag):  # type: ignore
            return cls[list]._parse_obj(obj)  # type: ignore
        if obj["type"] == QA.type_enum.join:  # type: ignore
            return cls[dict]._parse_obj(obj)  # type: ignore
        else:
            return cls._parse_obj(obj)  # type: ignore

    @classmethod
    def _parse_obj(cls: Type["Model"], obj: Any) -> "Model":
        return super().parse_obj(obj)  # type: ignore


class QAINCEL(BaseModel):
    class Config:
        json_encoders = {ObjectId: lambda v: str(v)}

    id: StrObjectId
    is_correct: bool
    answer: list[str]


class QAINC(BaseModel):
    class Config:
        json_encoders = {ObjectId: lambda v: str(v)}

    type: str
    question: str
    title: str
    answers: list[QAINCEL]
