from pymongo.collection import Collection

from arya_backend.auth import verify_password
from arya_backend.db.user import User


def test_user_create_if_not_exist(
    get_user_col: Collection, user_crud: User, user_dict: dict[str, str]
):
    assert get_user_col.count_documents({}) == 0
    _id = user_crud.create(**user_dict)
    assert _id is not None
    assert get_user_col.count_documents({}) == 1
    user = get_user_col.find_one()
    assert isinstance(user, dict)
    assert user["username"] == user_dict["username"]
    assert user["_id"] == _id
    assert verify_password(user_dict["password"], user["hashed_password"])
    assert user["scopes"] == ["qa:add"]


def test_user_create_if_exist(
    get_user_col: Collection, user_crud: User, user_dict: dict[str, str]
):
    assert get_user_col.count_documents({}) == 0
    user_crud.create(**user_dict)
    assert get_user_col.count_documents({}) == 1
    _id = user_crud.create(**user_dict)
    assert get_user_col.count_documents({}) == 1
    assert _id is None


def test_user_get_if_not_exist(
    get_user_col: Collection, user_crud: User, user_dict: dict[str, str]
):
    assert get_user_col.count_documents({}) == 0
    user = user_crud.get(username=user_dict["username"])
    assert user is None


def test_user_get_if_exist(
    get_user_col: Collection, user_crud: User, user_dict: dict[str, str]
):
    assert get_user_col.count_documents({}) == 0
    _id = user_crud.create(**user_dict)
    assert get_user_col.count_documents({}) == 1
    user = user_crud.get(username=user_dict["username"])
    assert user is not None
    assert isinstance(user, dict)
    assert _id == user["_id"]
