import pytest

from arya_backend.auth import create_access_token
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


@pytest.fixture
def get_auth_header(user_crud: User, user_dict: dict[str, str]):
    user_crud.create(**user_dict)
    token = create_access_token(data={"sub": user_dict["username"], "scopes": ""})
    return {"Authorization": f"Bearer {token}"}
