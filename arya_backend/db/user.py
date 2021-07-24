from pymongo.errors import DuplicateKeyError

from arya_backend import auth
from arya_backend.db import client

COLLECTION_NAME = "Users"


collection = client.get_database().get_collection(COLLECTION_NAME)
collection.create_index("username", unique=True)


class User:
    def __init__(self) -> None:
        self.client = client

    def get(self, username: str):
        return (
            self.client.get_database()
            .get_collection(COLLECTION_NAME)
            .find_one({"username": username})
        )

    def create(self, username: str, password: str):
        try:
            return (
                self.client.get_database()
                .get_collection(COLLECTION_NAME)
                .insert_one(
                    {
                        "username": username,
                        "hashed_password": auth.get_password_hash(password),
                        "scopes": ["qa:add"],
                    }
                )
                .inserted_id
            )
        except DuplicateKeyError:
            return None
