from typing import Optional

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from arya_backend import auth
from arya_backend.db import client

USERS_COLLECTION_NAME = "Users"


collection = client.get_database().get_collection(USERS_COLLECTION_NAME)
collection.create_index("username", unique=True)


class User:
    def __init__(self) -> None:
        self._client = client

    def get(self, username: str):
        return (
            self._client.get_database()
            .get_collection(USERS_COLLECTION_NAME)
            .find_one({"username": username})
        )

    def create(self, username: str, password: str) -> Optional[ObjectId]:
        try:
            _id = (
                self._client.get_database()
                .get_collection(USERS_COLLECTION_NAME)
                .insert_one(
                    {
                        "username": username,
                        "hashed_password": auth.get_password_hash(password),
                        "scopes": ["qa:add"],
                    }
                )
                .inserted_id
            )
            if isinstance(_id, ObjectId):
                return _id
        except DuplicateKeyError:
            return None

    @staticmethod
    def create_index():
        collection.create_index("username", unique=True)
