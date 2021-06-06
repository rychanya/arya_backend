import re
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from pydantic import parse_obj_as
from pymongo.collation import Collation

from arya_backend.db import MONGO_DB_NAME, client
from arya_backend.models.qa import QA

collection = client.get_database(MONGO_DB_NAME).get_collection("QA")
collection.create_index("question", collation=Collation(locale="ru", strength=2))


def parse_highlight(doc, q: str):
    patern = re.compile(f"({q})", flags=re.IGNORECASE)

    def to_highlight(text: str):
        if patern.match(text):
            return {"value": text, "type": "hit"}
        else:
            return {"value": text, "type": "text"}

    split = map(to_highlight, filter(lambda val: val, patern.split(doc["question"])))
    return {"question": list(split)}


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
    print(collection.aggregate(pipeline=[pipeline, {"$count": "count"}]))
    docs = list(
        collection.aggregate(
            pipeline=[pipeline, {"$skip": (page - 1) * LIMIT}, {"$limit": LIMIT}]
        )
    )
    return parse_obj_as(list[QA], docs)


def get(id: str) -> Optional[QA]:
    try:
        _id = ObjectId(id)
    except (InvalidId, TypeError):
        return
    doc = collection.find_one({"_id": _id})
    if doc:
        return QA.parse_obj(doc)
