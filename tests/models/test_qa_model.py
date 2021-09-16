import pytest
from pydantic import ValidationError, parse_obj_as

from arya_backend.models.qa import QA, ManyAnswer, OneAnswer


@pytest.fixture
def qa_dict():
    def _qa_dict(type: QA.type_enum = QA.type_enum.one):
        if type == QA.type_enum.one:
            return {
                "id": None,
                "question": "question",
                "answers": ["1", "2"],
                "extra_answers": [],
                "correct": "1",
                "incorrect": ["2"],
                "type": QA.type_enum.one,
                "incomplete": False,
            }
        elif type == QA.type_enum.many:
            return {
                "id": None,
                "question": "question",
                "answers": ["1", "2"],
                "extra_answers": [],
                "correct": ("1"),
                "incorrect": [("2")],
                "type": QA.type_enum.many,
                "incomplete": False,
            }
        elif type == QA.type_enum.drag:
            return {
                "id": None,
                "question": "question",
                "answers": ["1", "2"],
                "extra_answers": [],
                "correct": ["1", "2"],
                "incorrect": [["2", "1"]],
                "type": QA.type_enum.drag,
                "incomplete": False,
            }
        if type == QA.type_enum.join:
            return {
                "id": None,
                "question": "question",
                "answers": ["1", "2"],
                "extra_answers": ["a", "b"],
                "correct": (("1", "a"), ("2", "b")),
                "incorrect": [],
                "type": QA.type_enum.join,
                "incomplete": False,
            }
        else:
            raise ValueError

    return _qa_dict


@pytest.mark.parametrize(
    "type", (QA.type_enum.one, QA.type_enum.many, QA.type_enum.drag, QA.type_enum.join)
)
def test_norml_qa(type, qa_dict):
    qa_dict = qa_dict(type)
    QA.parse_obj(qa_dict)
    with pytest.raises(ValidationError):
        qa_dict.pop("type")
        QA.parse_obj(qa_dict)


@pytest.mark.parametrize(
    "correct,incorrect",
    [
        # one
        ("1", [["1"]]),
        ("1", [{"1"}]),
        ("1", [{"1": "1"}]),
        # many
        (["1"], ["1"]),
        (["1"], [{"1"}]),
        (["1"], [{"1": "1"}]),
        # drag
        ({"1"}, ["1"]),
        ({"1"}, [["1"]]),
        ({"1"}, [{"1": "1"}]),
        # join
        (("1", "1"), ["1"]),
        (("1", "1"), [{"1"}]),
        (("1", "1"), [["1"]]),
    ],
)
def test_consistency(correct, incorrect, qa_dict):
    qa_dict = qa_dict()
    qa_dict["incorrect"] = incorrect
    qa_dict["correct"] = correct
    with pytest.raises(ValidationError):
        QA.parse_obj(qa_dict)


def test_extra_answers_validation(qa_dict):
    qa_dict_one = qa_dict()
    qa_dict_one["extra_answers"] = ["1"]
    with pytest.raises(ValidationError):
        QA.parse_obj(qa_dict_one)
    qa_dict_join = qa_dict(QA.type_enum.join)
    assert len(qa_dict_join["extra_answers"]) == len(qa_dict_join["answers"])
    QA.parse_obj(qa_dict_join)
    qa_dict_join["extra_answers"] = ["a", "b", "c"]
    assert len(qa_dict_join["extra_answers"]) != len(qa_dict_join["answers"])
    with pytest.raises(ValidationError):
        QA.parse_obj(qa_dict_join)


@pytest.mark.parametrize(
    "type,incomplete,raised",
    [
        (QA.type_enum.one, True, False),
        (QA.type_enum.drag, True, True),
        (QA.type_enum.join, True, True),
        (QA.type_enum.many, True, False),
        (QA.type_enum.one, False, False),
        (QA.type_enum.drag, False, False),
        (QA.type_enum.join, False, False),
        (QA.type_enum.many, False, False),
    ],
)
@pytest.mark.parametrize("has_incorrect", (True, False))
def test_incomplete_validation(type, incomplete, raised, has_incorrect, qa_dict):
    qa_dict = qa_dict(type)
    qa_dict["incomplete"] = incomplete
    if has_incorrect:
        qa_dict["correct"] = None
    else:
        qa_dict["incorrect"] = []
    if raised:
        with pytest.raises(ValidationError):
            QA.parse_obj(qa_dict)
    else:
        QA.parse_obj(qa_dict)


def test_dict(qa_dict):
    qa = QA.parse_obj(qa_dict()).to_mongo()
    assert isinstance(qa["incorrect"], list)
