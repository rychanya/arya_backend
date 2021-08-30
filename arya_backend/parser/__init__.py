from typing import Tuple, Union

from bson.objectid import ObjectId

from arya_backend.db.QA import QACRUD
from arya_backend.db.upload_QA import UploadCRUD

# from arya_backend.db.QA import get_or_create_qa_incomplite, is_exists
# from arya_backend.db.upload_QA import set_data
from arya_backend.models.qa import QA
from arya_backend.models.upload_QA import Payload


def parse_type(type: str) -> str:
    if type == "единственный выбор":
        return QA.type_enum.one.value
    elif type == "множественный выбор":
        return QA.type_enum.many.value
    else:
        raise TypeError


def parse_answers(
    answer: str, answer_type: str
) -> Union[Tuple[list[str], str], Tuple[list[str], list[str]]]:
    if answer_type == QA.type_enum.one:
        return ([answer], answer)
    elif answer_type == QA.type_enum.many:
        answers = answer.split(";\r\r\n")
        return (answers, answers)
    else:
        raise TypeError


def parse_correct(value: str) -> bool:
    if value == "+":
        return True
    elif value == "-":
        return False
    else:
        raise TypeError


def normalize_cp1251(s: str) -> str:
    try:
        return s.encode("cp1251").decode("utf8")
    except UnicodeDecodeError:
        return s


def row_iter(payload: list[Payload]):
    for row in payload:
        try:
            title = normalize_cp1251(row.title)
            type = parse_type(row.type)
            answers, normalize_answer = parse_answers(row.answer, type)
            question = row.question
            is_correct = parse_correct(row.is_correct)
            qa_dict = {
                "tags": {"title": title},
                "type": type,
                "answers": answers,
                "question": question,
                "incomplete": True,
            }
            if is_correct:
                qa_dict["correct"] = normalize_answer
            else:
                qa_dict["incorrect"] = [normalize_answer]
            yield qa_dict
        except (TypeError, KeyError):
            pass


def parse(id: ObjectId):
    payload = UploadCRUD().get_by_id(id)
    if payload is None:
        return
    data = [QA.parse_obj(qa) for qa in row_iter(payload.data)]
    for d in data:
        db = QACRUD()
        print(len(db.get_or_create(d)))
    # set_data(id, data)
