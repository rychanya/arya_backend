from typing import Optional

from bson.objectid import ObjectId
from pydantic import parse_obj_as

from arya_backend.db import MONGO_DB_NAME, client
from arya_backend.models.upload_QA import Payload, Upload

collection = client.get_database(MONGO_DB_NAME).get_collection("UPLOAD")


class UploadCRUD:
    def create(self, user_id: ObjectId, payload: list[Payload]):
        return collection.insert_one(
            {"by": user_id, "data": [p.dict() for p in payload]}
        ).inserted_id

    def get_by_user(self, user_id: ObjectId) -> list[Upload]:
        return parse_obj_as(
            list[Upload], list(collection.aggregate([{"$match": {"by": user_id}}]))
        )

    def get_by_id(self, id: ObjectId) -> Optional[Upload]:
        doc = collection.find_one({"_id": id})
        if doc:
            return Upload.parse_obj(doc)
