import math
from typing import Optional, Union

from bson import ObjectId
from bson.errors import InvalidId
from pydantic import parse_obj_as
from pymongo import ReturnDocument
from pymongo.collation import Collation

from arya_backend.db import MONGO_DB_NAME, client
from arya_backend.models.qa import QA, QAIncomplete

collection = client.get_database(MONGO_DB_NAME).get_collection("QA")
collection_incomplete = client.get_database(MONGO_DB_NAME).get_collection("QA_INC")


collection.create_index("question", collation=Collation(locale="ru", strength=2))


def search(q: str, page: int = 1):
    LIMIT = 10
    if page < 1:
        page = 1
    pipeline = {
        "$match": {
            "correct": {"$exists": True},
            "question": {"$regex": f".*{q}.*", "$options": "i"},
        }
    }
    docs_count = list(collection.aggregate(pipeline=[pipeline, {"$count": "count"}]))[
        0
    ]["count"]
    paginator = {"current": page, "all": math.ceil(docs_count / LIMIT)}
    docs = list(
        collection.aggregate(
            pipeline=[pipeline, {"$skip": (page - 1) * LIMIT}, {"$limit": LIMIT}]
        )
    )
    return (parse_obj_as(list[QA], docs), paginator)


def get(id: str) -> Optional[QA]:
    try:
        _id = ObjectId(id)
    except (InvalidId, TypeError):
        return
    doc = collection.find_one({"_id": _id})
    if doc:
        return QA.parse_obj(doc)


def is_exists(type: str, answer: list[str], question: str):
    filter = {
        "type": type,
        "question": question,
    }
    if len(answer) == 1:
        filter.update({"correct": answer[0]})
    else:
        filter.update(  # type: ignore
            {
                "correct": {"$all": [{"$elemMatch": {"$eq": el}} for el in answer]},
            }
        )
    qa = collection.find_one(filter=filter)
    if qa:
        return qa["_id"]


def get_or_create_qa_incomplite(qa: QAIncomplete):
    filter = {
        "question": qa.question,
        "type": qa.type,
        "title": qa.title,
        "is_correct": qa.is_correct,
        "answer": {"$all": [{"$elemMatch": {"$eq": el}} for el in qa.answer]},
    }
    with client.start_session() as session:
        with session.start_transaction() as transaction:
            ...
    doc = collection_incomplete.find_one_and_update(
        filter=filter,
        update={
            "$setOnInsert": {"answer": qa.answer, "create": qa.by[0]},
            "$addToSet": {"by": qa.by[0]},
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    if doc:
        return doc["_id"]
