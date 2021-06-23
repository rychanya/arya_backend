import math
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from pydantic import parse_obj_as
from pymongo.collation import Collation
from pymongo import ReturnDocument

from arya_backend.db import MONGO_DB_NAME, client
from arya_backend.models.qa import QA

collection = client.get_database(MONGO_DB_NAME).get_collection("QA")

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


# def get_or_create_incomplete(qa: Optional[QA]) -> Tuple[Optional[QA], Optional[bool]]:
#     if qa is None:
#         return (None, None)
#     if qa.correct is not None:
#         filter = qa.dict(include={"question", "type", "correct"})
#         update = qa.tags.get("title")
#         if update:
#             update = {"$set": {"tags.title": update}}
#             doc = collection.find_one_and_update(
#                 filter=filter, update=update, return_document=ReturnDocument.AFTER
#             )
#         else:
#             doc = collection.find_one(filter=filter)
#         if doc:
#             return (QA.parse_obj(doc), False)
#         else:
#             qa.tags.update({"incomplete": ""})
#             payload = qa.dict(by_alias=True, exclude_none=True)
#             _id = collection.insert_one(document=payload).inserted_id  # type: ignore
#             return (QA.parse_obj(collection.find_one({"_id": _id})), True)
#     else:
#         filter = qa.dict(include={"question", "type", "incorrect"})
#         update = qa.tags.get("title")
#         if update:
#             update = {"$set": {"tags.title": update}}
#             doc = collection.find_one_and_update(
#                 filter=filter, update=update, return_document=ReturnDocument.AFTER
#             )
#         else:
#             doc = collection.find_one(filter=filter)
#         if doc:
#             return (QA.parse_obj(doc), False)
#         else:
#             qa.tags.update({"incomplete": ""})
#             payload = qa.dict(by_alias=True, exclude_none=True)
#             _id = collection.insert_one(document=payload).inserted_id  # type: ignore
#             return (QA.parse_obj(collection.find_one({"_id": _id})), True)


# def get_incomplete(qa: QA) -> Optional[QA]:
#     filter = qa.dict(include={"type", "question"})
#     filter.update(
#         {
#             "answers": {
#                 "$all": [{"$elemMatch": {"$eq": answer}} for answer in qa.answers]
#             }
#         }
#     )
#     update = {
#         '$set': {'tags.title': qa.tags.get('title')},
#         '$setOnInsert': {'tags.incomplete': True}
#     }
#     if qa.correct:
#         filter.update({"correct": qa.correct})
#     elif qa.incorrect:
#         update.update({'$addToSet': {'incorrect': qa.incorrect[0]}})
#     else:
#         return
    
#     collection.find_one_and_update(filter=filter, update=update, upsert=True, return_document=ReturnDocument.AFTER)
