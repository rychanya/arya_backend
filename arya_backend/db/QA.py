from itertools import chain
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from pydantic import parse_obj_as

from arya_backend.db import MONGO_DB_NAME, client
from arya_backend.models.qa import QA, QA_with_highlights

collection = client.get_database(MONGO_DB_NAME).get_collection("QA")


def parse_highlight(doc, q: str):
    def to_highlight(text: str):
        if not text:
            return []
        return [{"value": text, "type": "text"}]

    prefix, _, sufix = doc["question"].partition(q)
    return {
        "question": list(
            chain(
                to_highlight(prefix), [{"value": q, "type": "hit"}], to_highlight(sufix)
            )
        )
    }


def search(q: str):
    pipeline = [
        {"$match": {"correct": {"$exists": True}, "question": {"$regex": f".*{q}.*"}}},
        {"$limit": 10},
        {
            "$set": {
                "highlights": {"$meta": "searchHighlights"},
            }
        },
    ]
    docs = list(collection.aggregate(pipeline=pipeline))
    for doc in docs:
        doc["highlights"] = parse_highlight(doc, q)

    return parse_obj_as(list[QA_with_highlights], docs)


def get(id: str) -> Optional[QA]:
    try:
        _id = ObjectId(id)
    except (InvalidId, TypeError):
        return
    doc = collection.find_one({"_id": _id})
    if doc:
        return QA.parse_obj(doc)
