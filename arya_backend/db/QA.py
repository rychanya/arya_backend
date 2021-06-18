import math
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

def get_or_create(qa: Optional[QA])-> Optional[QA]:
    if qa is None:
        return None
    filter = qa.dict(include={'question', 'type', 'correct'})
    # collection.find_one_and_update(filter=filter, update={})
    doc = collection.find_one(filter=filter)
    return doc