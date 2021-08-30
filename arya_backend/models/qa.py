from enum import Enum
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from bson import ObjectId
from pydantic import BaseModel, Field, constr, validator
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

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class OneAnswer(BaseModel):
    __root__: constr(min_length=1)  # type: ignore

    def __str__(self) -> str:
        return self.__root__

    def __bool__(self):
        return bool(self.__root__)


class ManyAnswer(BaseModel):
    __root__: set[constr(min_length=1)]  # type: ignore

    def __iter__(self):
        return iter(self.__root__)

    def __bool__(self):
        return bool(self.__root__)

    def __len__(self):
        return len(self.__root__)


class DragAnswer(BaseModel):
    __root__: list[constr(min_length=1)]  # type: ignore

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]

    def __bool__(self):
        return bool(self.__root__)

    def __len__(self):
        return len(self.__root__)


class JoinAnswer(BaseModel):
    __root__: Dict[constr(min_length=1), constr(min_length=1)]  # type: ignore

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]

    def __bool__(self):
        return bool(self.__root__)

    def __len__(self):
        return len(self.__root__)

    def items(self):
        return self.__root__.items()


AnswerType = TypeVar("AnswerType", OneAnswer, ManyAnswer, JoinAnswer, DragAnswer)
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
    incomplete: bool = False

    @validator("correct")
    def check_correct(cls, correct, values):
        type = values.get("type")
        answers = values.get("answers")
        extra_answers = values.get("extra_answers")
        if correct is None:
            return correct
        if type is None or answers is None or extra_answers is None:
            raise ValueError("can not validate correct")
        QA._validate_answer(correct, type, answers, extra_answers)
        return correct

    @validator("incorrect")
    def check_incorrect(cls, incorrect, values):
        type = values.get("type")
        answers = values.get("answers")
        extra_answers = values.get("extra_answers")
        if type is None or answers is None or extra_answers is None:
            raise ValueError("can not validate correct")
        for ans in incorrect:
            QA._validate_answer(ans, type, answers, extra_answers)
        return incorrect

    @staticmethod
    def _validate_answer(answer, type, answers, extra_answers=[]):
        if type == QA.type_enum.one and answer not in answers:
            raise ValueError("correct  must be in answers")
        elif type == QA.type_enum.many and not answer.issubset(answers):
            raise ValueError("correct must be subset of answers")
        elif type == QA.type_enum.drag and set(answer) != set(answers):
            raise ValueError("correct must contains all answers")
        elif type == QA.type_enum.join and (
            set(answer.keys()) != set(answers)
            or set(answer.values()) != set(extra_answers)
        ):
            raise ValueError("correct must contains all answers/extra_answers")

    @validator("incomplete")
    def check_incomplete(cls, incomplete, values):
        type = values.get("type")
        if type is None:
            raise ValueError("type missing")
        if incomplete:
            if type in (QA.type_enum.drag, QA.type_enum.join):
                raise ValueError("qa[join] or qa[drag] can not be incomplete")
            elif bool(values["correct"]) == bool(values["incorrect"]):
                raise ValueError(
                    "incomplete qa can contain only correct or incorect answer, not both"
                )
        return incomplete

    @validator("extra_answers")
    def check_extra_answers(cls, extra_answers, values):
        type = values.get("type")
        if type is None:
            raise ValueError("type missing")
        if type == QA.type_enum.join:
            if not extra_answers:
                raise ValueError("qa[join] must contain extra_answers")
            if len(extra_answers) != len(values["answers"]):
                raise ValueError("len of answers and extra_answers must equals")
        elif extra_answers:
            raise ValueError("only qa[join] can contain extra_answers")
        return extra_answers

    def is_correct(self):
        return bool(self.correct)

    @classmethod
    def parse_obj(cls: Type["Model"], obj: Any) -> "Model":
        type = obj.get("type")
        if type is None:
            return cls._parse_obj(obj)  # type: ignore
        if type == cls.type_enum.one:  # type: ignore
            return cls[str]._parse_obj(obj)  # type: ignore
        elif type == cls.type_enum.many:  # type: ignore
            return cls[set]._parse_obj(obj)  # type: ignore
        elif type == cls.type_enum.drag:  # type: ignore
            return cls[list]._parse_obj(obj)  # type: ignore
        elif type == cls.type_enum.join:  # type: ignore
            return cls[dict]._parse_obj(obj)  # type: ignore

    @classmethod
    def _parse_obj(cls: Type["Model"], obj: Any) -> "Model":
        return super().parse_obj(obj)  # type: ignore
