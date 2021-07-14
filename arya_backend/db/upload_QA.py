from bson.objectid import ObjectId
from pydantic import parse_obj_as

from arya_backend.db import MONGO_DB_NAME, client
from arya_backend.models.upload_QA import Upload

collection = client.get_database(MONGO_DB_NAME).get_collection("UPLOAD")


def create(user_id: ObjectId):
    return collection.insert_one({"by": user_id}).inserted_id


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
    return parse_obj_as(
        list[Upload], list(collection.aggregate([{"$match": {"by": user_id}}]))
    )


def get_by_id(id: ObjectId):
    return collection.find_one({"_id": id})


def set_data(id: ObjectId, data):
    collection.update_one({"_id": id}, {"$set": {"data": data}})
