import pytest

from arya_backend.db import client
from arya_backend.db.user import COLLECTION_NAME, User


@pytest.fixture
def user_crud():
    return User()


@pytest.fixture
def user_dict():
    return {"username": "user", "password": "pass"}


@pytest.fixture
def get_user_col():
    collection = client.get_database().get_collection(COLLECTION_NAME)
    collection.delete_many({})
    yield collection
    collection.delete_many({})
