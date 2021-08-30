from typing import Optional

import pytest
from pymongo.collection import Collection

from arya_backend.db.QA import QACRUD
from arya_backend.models.qa import QA


@pytest.fixture
def iqa():
    return QA(
        incomplete=0,
        type=QA.type_enum.one,
        question="question",
        answers=["1", "2", "3"],
        correct="1",
    )


@pytest.fixture
def qa():
    return QA(
        incomplete=False,
        type=QA.type_enum.one,
        question="question",
        answers=["1", "2", "3"],
        correct="1",
    )


# def test_add_iqa_if_it_not_exist(get_qa_col: Collection, qa_crud: QACRUD, iqa: QA):
#     assert get_qa_col.count_documents({}) == 0
#     id, is_new = qa_crud.get_or_create(iqa)
#     assert is_new == True
#     assert get_qa_col.count_documents({}) == 1
#     assert id is not None
#     res_dict: Optional[dict] = get_qa_col.find_one({"_id": id})
#     assert res_dict is not None
#     res_dict.pop("_id")
#     assert res_dict == iqa.dict(exclude={"id"})


# def test_add_iqa_if_it_exist(get_qa_col: Collection, qa_crud: QACRUD, iqa: QA):
#     assert get_qa_col.count_documents({}) == 0
#     exists_id = get_qa_col.insert_one(iqa.dict(exclude_none=True)).inserted_id
#     assert get_qa_col.count_documents({}) == 1
#     id, is_new = qa_crud.get_or_create(iqa)
#     assert is_new == False
#     assert id == exists_id

# qa iqa add iqa -> iqa update
# qa iqa add qa -> qa update
# qa -iqa add iqa -> iqa insert
# qa -iqa add qa -> qa update
# -qa -iqa add iqa -> iqa insert
# -qa -iqa add qa -> qa insert
# -qa iqa add iqa -> update iqa
# -qa iqa add qa ->insert qa
