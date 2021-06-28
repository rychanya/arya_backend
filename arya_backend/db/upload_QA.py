from arya_backend.db import MONGO_DB_NAME, client
from arya_backend.models.upload_QA import Upload

collection = client.get_database(MONGO_DB_NAME).get_collection("UPLOAD")


def upload(upload: Upload) -> str:
    _id = collection.insert_one(document=upload.dict(exclude_none=True)).inserted_id
    return str(_id)
