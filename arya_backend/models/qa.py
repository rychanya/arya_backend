from enum import Enum
from itertools import chain, combinations, permutations, product
from typing import Any, Dict, Generic, Optional, Type, TypeVar, Union

from bson import ObjectId
from pydantic import BaseModel, Field, validator
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
    __root__: str

    def __str__(self) -> str:
        return self.__root__

    def __bool__(self):
        return bool(self.__root__)

    def __eq__(self, other: Any) -> bool:
        if other is None:
            return False
        if isinstance(other, OneAnswer):
            return self.__root__ == other.__root__
        elif isinstance(other, str):
            return self.__root__ == other
        else:
            raise NotImplementedError

    def __hash__(self) -> int:
        return self.__root__.__hash__()

    def to_mongo(self):
        return self.__root__


class ManyAnswer(BaseModel):
    __root__: frozenset

    def __iter__(self):
        return iter(self.__root__)

    def __bool__(self):
        return bool(self.__root__)

    def __len__(self):
        return len(self.__root__)

    def __eq__(self, other: Any) -> bool:
        if other is None:
            return False
        if isinstance(other, ManyAnswer):
            return self.__root__ == other.__root__
        elif isinstance(other, (set, frozenset)):
            return self.__root__ == other
        elif isinstance(other, (list, tuple)):
            return self.__root__ == set(other)
        else:
            raise NotImplementedError

    def __hash__(self) -> int:
        return self.__root__.__hash__()

    def __contains__(self, item):
        return item in self.__root__

    def to_mongo(self):
        return list(self.__root__)

    def issubset(self, another):
        return self.__root__.issubset(another)


class DragAnswer(BaseModel):
    __root__: tuple[str, ...]

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]

    def __bool__(self):
        return bool(self.__root__)

    def __len__(self):
        return len(self.__root__)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, DragAnswer):
            return self.__root__ == other.__root__
        elif isinstance(other, (list, tuple)):
            return self.__root__ == other
        else:
            raise NotImplementedError

    def __hash__(self) -> int:
        return self.__root__.__hash__()

    def to_mongo(self):
        return list(self.__root__)


class JoinAnswer(BaseModel):
    __root__: frozenset[tuple[str, str]]

    def __iter__(self):
        return iter(self.__root__)

    def __bool__(self):
        return bool(self.__root__)

    def __len__(self):
        return len(self.__root__)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, JoinAnswer):
            return self.__root__ == other.__root__
        else:
            raise NotImplementedError

    def __hash__(self) -> int:
        return self.__root__.__hash__()

    def to_mongo(self):
        return dict(self.__root__)


AnswerType = TypeVar("AnswerType", OneAnswer, ManyAnswer, JoinAnswer, DragAnswer)
Model = TypeVar("Model", bound="BaseModel")


class QA(GenericModel, Generic[AnswerType]):
    class type_enum(str, Enum):
        one = "Выберите один правильный вариант"
        many = "Выберите все правильные варианты"
        drag = "Перетащите варианты так, чтобы они оказались в правильном порядке"
        join = "Соедините соответствия справа с правильными вариантами"  # type: ignore

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: lambda v: str(v), frozenset: lambda v: list(v)}
        allow_mutation = False

    id: StrObjectId = Field(None, alias="_id")
    type: type_enum
    question: str
    answers: list[str]
    extra_answers: list[str] = []
    correct: Optional[AnswerType]
    incorrect: frozenset[AnswerType] = frozenset()
    tags: Dict[str, str] = {}
    incomplete: bool = False

    def to_mongo(self, exclude_id=True, exclude: set = set()):
        if exclude_id:
            exclude.add("id")
        res = self.dict(exclude=exclude, by_alias=True)
        res["incorrect"] = list(res["incorrect"])
        return res

    def _get_all_answers(self):
        if self.type == QA.type_enum.one:
            return set(map(OneAnswer.parse_obj, self.answers))
        elif self.type == QA.type_enum.many:
            return set(
                map(
                    ManyAnswer.parse_obj,
                    chain(
                        *[
                            combinations(self.answers, n)
                            for n in range(1, len(self.answers) + 1)
                        ]
                    ),
                )
            )
        elif self.type == QA.type_enum.drag:
            return set(
                map(
                    DragAnswer.parse_obj,
                    permutations(self.answers),
                )
            )
        elif self.type == QA.type_enum.join:
            return set(
                map(
                    JoinAnswer.parse_obj,
                    (
                        frozenset(zip(*i))
                        for i in product(
                            permutations(self.answers), permutations(self.extra_answers)
                        )
                    ),
                )
            )
        else:
            raise ValueError

    def get_answer(self) -> Union[OneAnswer, ManyAnswer, DragAnswer, JoinAnswer]:
        if self.correct is not None:
            return self.correct
        answers = self._get_all_answers().difference(self.incorrect)
        if not answers:
            answers = self._get_all_answers()
        ans = answers.pop()
        return ans

    @validator("correct", pre=True)
    def check_pre_correct(cls, correct, values):
        _type = values.get("type")
        if correct is None:
            return None
        if _type == QA.type_enum.many or _type == QA.type_enum.join:
            return frozenset(correct)
        return correct

    @validator("incorrect", pre=True)
    def check_pre_incorrect(cls, incorrect, values):
        _type = values.get("type")
        if _type == QA.type_enum.many or _type == QA.type_enum.join:
            return frozenset((frozenset(v) for v in incorrect))
        return incorrect

    @validator("correct")
    def check_correct(cls, correct, values):
        _type = values.get("type")
        answers = values.get("answers")
        extra_answers = values.get("extra_answers")
        if correct is None:
            return correct
        if _type is None or answers is None or extra_answers is None:
            raise ValueError("can not validate correct")
        QA._validate_answer(correct, _type, answers, extra_answers)
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
        if type == QA.type_enum.one and str(answer) not in answers:
            raise ValueError("correct  must be in answers")
        elif type == QA.type_enum.many and not answer.issubset(answers):
            raise ValueError("correct must be subset of answers")
        elif type == QA.type_enum.drag and set(answer) != set(answers):
            raise ValueError("correct must contains all answers")
        elif type == QA.type_enum.join and (
            set((v[0] for v in answer)) != set(answers)
            or set((v[1] for v in answer)) != set(extra_answers)
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
            else:
                correct = values.get("correct")
                incorrect = values.get("incorrect")
                if correct is None and incorrect is None:
                    raise ValueError(" can not validate incomplete")
                if bool(correct) == bool(incorrect):
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
            return cls[OneAnswer]._parse_obj(obj)  # type: ignore
        elif type == cls.type_enum.many:  # type: ignore
            return cls[ManyAnswer]._parse_obj(obj)  # type: ignore
        elif type == cls.type_enum.drag:  # type: ignore
            return cls[DragAnswer]._parse_obj(obj)  # type: ignore
        elif type == cls.type_enum.join:  # type: ignore
            return cls[JoinAnswer]._parse_obj(obj)  # type: ignore
        else:
            raise ValueError

    @classmethod
    def _parse_obj(cls: Type["Model"], obj: Any) -> "Model":
        return super().parse_obj(obj)  # type: ignore
