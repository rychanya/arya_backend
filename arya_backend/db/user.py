from typing import Optional

from pymongo.errors import DuplicateKeyError

from arya_backend import auth
from arya_backend.db import MONGO_DB_NAME, client
from arya_backend.models.auth import UserInDB

collection = client.get_database(MONGO_DB_NAME).get_collection("Users")
# collection.create_index("username", unique=True)


def get(username: str) -> Optional[UserInDB]:
    user = collection.find_one(filter={"username": username})
    if user:
        return UserInDB.parse_obj(user)


def create(username: str, password: str) -> Optional[UserInDB]:
    payload = {
        "username": username,
        "hashed_password": auth.get_password_hash(password),
    }
    try:
        collection.insert_one(document=payload)
        return get(username)
    except DuplicateKeyError:
        ...
