import pytest
from pymongo.collection import Collection

from arya_backend.auth import verify_password
from arya_backend.db import client
from arya_backend.db.user import COLLECTION_NAME, User


@pytest.fixture
def get_collection():
    collection = client.get_database().get_collection(COLLECTION_NAME)
    collection.delete_many({})
    return collection


@pytest.fixture
def crud():
    return User()


@pytest.fixture
def user_dict():
    return {"username": "user", "password": "pass"}


def test_user_create_if_not_exist(
    get_collection: Collection, crud: User, user_dict: dict[str, str]
):
    assert get_collection.count_documents({}) == 0
    _id = crud.create(**user_dict)
    assert _id is not None
    assert get_collection.count_documents({}) == 1
    user = get_collection.find_one()
    assert isinstance(user, dict)
    assert user["username"] == user_dict["username"]
    assert user["_id"] == _id
    assert verify_password(user_dict["password"], user["hashed_password"])
    assert user["scopes"] == ["qa:add"]


def test_user_create_if_exist(
    get_collection: Collection, crud: User, user_dict: dict[str, str]
):
    assert get_collection.count_documents({}) == 0
    crud.create(**user_dict)
    assert get_collection.count_documents({}) == 1
    _id = crud.create(**user_dict)
    assert get_collection.count_documents({}) == 1
    assert _id is None


def test_user_get_if_not_exist(
    get_collection: Collection, crud: User, user_dict: dict[str, str]
):
    assert get_collection.count_documents({}) == 0
    user = crud.get(username=user_dict["username"])
    assert user is None


def test_user_get_if_exist(
    get_collection: Collection, crud: User, user_dict: dict[str, str]
):
    assert get_collection.count_documents({}) == 0
    _id = crud.create(**user_dict)
    assert get_collection.count_documents({}) == 1
    user = crud.get(username=user_dict["username"])
    assert user is not None
    assert isinstance(user, dict)
    assert _id == user["_id"]
