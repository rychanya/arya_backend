import math
from os import PRIO_PGRP
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from pydantic import parse_obj_as
from pymongo import ReturnDocument
from pymongo.client_session import ClientSession
from pymongo.collation import Collation
from pymongo.collection import Collection

from arya_backend.db import MONGO_DB_NAME, client
from arya_backend.models.qa import QA, QAINC, QAIncomplete
from arya_backend.models.upload_QA import Foreign

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


def get_inc(id: str) -> Optional[QAIncomplete]:
    try:
        _id = ObjectId(id)
    except (InvalidId, TypeError):
        return
    doc = collection_incomplete.find_one({"_id": _id})
    if doc:
        return QAIncomplete.parse_obj(doc)


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


def get_or_create_qa_incomplite(qa: QAIncomplete) -> Foreign:
    def callback(session: ClientSession, qa: QAIncomplete):
        col: Collection = session.client.get_database(MONGO_DB_NAME).get_collection(
            "QA_INC"
        )
        filter = {
            "question": qa.question,
            "type": qa.type,
            "title": qa.title,
            "is_correct": qa.is_correct,
            "answer": {"$all": [{"$elemMatch": {"$eq": el}} for el in qa.answer]},
        }
        doc = col.find_one(filter)
        if doc is None:
            doc = col.insert_one(qa.dict(exclude_none=True)).inserted_id
            return Foreign(id=doc, col="QA_INC", new=True)
        doc = col.find_one_and_update(
            filter={"_id": doc["_id"]},
            update={
                "$addToSet": {"by": qa.by[0]},
            },
        )
        return Foreign(id=doc["_id"], col="QA_INC")

    with client.start_session() as session:
        return session.with_transaction(lambda s: callback(s, qa))


def searc_inc(q: str):
    pipeline = [
        {
            "$match": {
                "correct": {"$exists": True},
                "question": {"$regex": f".*{q}.*", "$options": "i"},
            }
        }
    ]
    doc = list(collection.aggregate(pipeline=pipeline))
    pipeline_inc = [
        {
            "$match": {
                "is_correct": True,
                "question": {"$regex": f".*{q}.*", "$options": "i"},
            }
        },
        {
            "$group": {
                "_id": {"type": "$type", "question": "$question", "title": "$title"},
                "answers": {
                    "$addToSet": {
                        "answer": "$answer",
                        "is_correct": "$is_correct",
                        "id": "$_id",
                    }
                },
            }
        },
        {
            "$project": {
                "answers": 1,
                "type": "$_id.type",
                "question": "$_id.question",
                "title": "$_id.title",
                "_id": 0,
            }
        },
    ]
    docs_inc = list(collection_incomplete.aggregate(pipeline=pipeline_inc))
    return [*parse_obj_as(list[QA], doc), *parse_obj_as(list[QAINC], docs_inc)]
