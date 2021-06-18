from openpyxl import load_workbook
from arya_backend.models.qa import QA
from functools import partial
from itertools import chain
from io import BytesIO


def parse_type(type: str) -> str:
    if type == "единственный выбор":
        return QA.type_enum.one.value
    elif type == "множественный выбор":
        return QA.type_enum.many.value
    else:
        raise TypeError


def parse_row(row, title: str):
    answers = row[4].split(";_x000D_\n")
    if row[2] == "+":
        payload = {
            "question": row[1],
            "type": parse_type(row[6]),
            "answers": answers,
            "tags": {"title": title},
            "correct": answers,
        }
        if payload["type"] == QA.type_enum.one:
            payload["correct"] = payload["correct"][0]
        return QA.parse_obj(payload)


def parse_xl(file):
    stream = BytesIO(file.read())
    wb = load_workbook(filename=stream, read_only=True)
    result = []
    for ws in wb.worksheets:
        title = str(ws.title)
        parse_with_title = partial(parse_row, title=title)
        qas = map(parse_with_title, ws.iter_rows(min_row=2, values_only=True))
        result = chain(result, qas)
    return list(result)
