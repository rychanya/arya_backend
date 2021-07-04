from itertools import chain

from bson.objectid import ObjectId

from arya_backend.db import MONGO_DB_NAME, client
from arya_backend.models.upload_QA import Upload

collection = client.get_database(MONGO_DB_NAME).get_collection("UPLOAD")


def create(upload: Upload):
    return collection.insert_one(
        upload.dict(exclude_none=True, by_alias=True)
    ).inserted_id


# def get_by_user(user: ObjectId):
#     upload1 = collection.aggregate(
#         [
#             {"$match": {"by": user}},
#             {"$unwind": "$data"},
#             {"$replaceRoot": {"newRoot": "$data"}},
#             {"$match": {"col": "QA"}},
#             {
#                 "$lookup": {
#                     "from": "QA",
#                     "localField": "id",
#                     "foreignField": "_id",
#                     "as": "qa",
#                 }
#             },
#         ]
#     )
#     upload2 = collection.aggregate(
#         [
#             {"$match": {"by": user}},
#             {"$unwind": "$data"},
#             {"$replaceRoot": {"newRoot": "$data"}},
#             {"$match": {"col": "QA_INC"}},
#             {
#                 "$lookup": {
#                     "from": "QA_INC",
#                     "localField": "id",
#                     "foreignField": "_id",
#                     "as": "qa",
#                 }
#             },
#         ]
#     )
#     return chain(upload1, upload2)


def get_by_user(user_id: ObjectId):
    return collection.aggregate([{"$match": {"by": user_id}}])
