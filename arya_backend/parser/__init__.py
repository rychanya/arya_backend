from functools import partial
from io import BytesIO
from typing import Union

from openpyxl import load_workbook

from arya_backend.models.qa import QA
from arya_backend.models.upload_QA import Upload, UploadQA


def parse_type(type: str) -> str:
    if type == "единственный выбор":
        return QA.type_enum.one.value
    elif type == "множественный выбор":
        return QA.type_enum.many.value
    else:
        raise TypeError


def parse_answer(
    answer: str, answer_type: str
) -> Union[str, list[str], dict[str, str]]:
    if answer_type == QA.type_enum.one:
        return answer
    elif answer_type == QA.type_enum.many:
        return answer.split(";_x000D_\n")
    else:
        raise TypeError


# def parse_answers(answer: Union[str, list[str], dict[str, str]]) -> list[str]:
#     if isinstance(answer, str):
#         return [answer]
#     elif isinstance(answer, list):
#         return answer
#     else:
#         raise TypeError


def parse_correct(value: str) -> bool:
    if value == "+":
        return True
    elif value == "-":
        return False
    else:
        raise TypeError


def parse_row(row, title: str):
    try:
        answer_type = parse_type(row[6])
        answer = parse_answer(row[4], answer_type)
        # answers = parse_answers(answer)
        question = row[1]
        is_correct = parse_correct(row[2])
        payload = {
            "question": question,
            "type": answer_type,
            # "answers": answers,
            "title": title,
            "is_correct": is_correct,
        }
    except (TypeError, KeyError):
        return None
    return UploadQA.parse_obj(payload)


def parse_xl(file):
    stream = BytesIO(file.read())
    wb = load_workbook(filename=stream, read_only=True)
    result = []
    for ws in wb.worksheets:
        title = str(ws.title)
        parse_with_title = partial(parse_row, title=title)
        qas = map(parse_with_title, ws.iter_rows(min_row=2, values_only=True))
        result.extend(qas)
    return list(result)
