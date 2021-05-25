from itertools import chain
from typing import Optional

from pydantic import parse_obj_as
from bson import ObjectId
from bson.errors import InvalidId

from arya_backend.db import MONGO_DB_NAME, client
from arya_backend.models.qa import QA_with_highlights, QA

collection = client.get_database(MONGO_DB_NAME).get_collection("QA")


def parse_highlight(doc):
    def parse_one(highlight):
        texts = highlight["texts"]
        union = "".join([text["value"] for text in texts])
        path = highlight["path"]
        return (texts, union, path)

    def recombine(origin: str, part, highlight):
        def tohighlight(value):
            if value:
                return [{"value": value, "type": "text"}]
            else:
                return []

        if origin == part:
            return highlight
        prefix, _, sufix = origin.partition(part)
        return list(chain(tohighlight(prefix), highlight, tohighlight(sufix)))

    return {
        path: recombine(doc[path], union, texts)
        for texts, union, path in map(parse_one, doc["highlights"])
    }


def search(q: str):
    pipeline = [
        {
            "$search": {
                "wildcard": {
                    "path": "question",
                    "query": f"*{q}*",
                },
                "highlight": {"path": "question"},
            }
        },
        {"$match": {"correct": {"$exists": True}}},
        {"$limit": 10},
        {
            "$set": {
                "highlights": {"$meta": "searchHighlights"},
            }
        },
    ]
    docs = list(collection.aggregate(pipeline=pipeline))
    for doc in docs:
        doc["highlights"] = parse_highlight(doc)

    return parse_obj_as(list[QA_with_highlights], docs)

def get(id: str) -> Optional[QA]:
    try:
        _id = ObjectId(id)
    except (InvalidId, TypeError):
        return
    doc = collection.find_one({'_id': _id})
    if doc:
        return QA.parse_obj(doc)
    