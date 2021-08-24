import pytest
from fastapi.testclient import TestClient
from pymongo.collection import Collection

from arya_backend.auth import decode_access_token
from arya_backend.db.user import User
from arya_backend.main import app

client = TestClient(app)


@pytest.mark.usefixtures("get_user_col")
def test_get_token_with_correct_credit(user_crud: User, user_dict: dict[str, str]):
    assert user_crud.create(**user_dict) is not None
    response = client.post("/user/token", data=user_dict)
    assert response.status_code == 200
    json = response.json()
    assert json["token_type"] == "bearer"
    token = json["access_token"]
    token_data = decode_access_token(token)
    assert token_data.username == user_dict["username"]


@pytest.mark.usefixtures("get_user_col")
def test_get_token_with_incorrect_credit(user_crud: User, user_dict: dict[str, str]):
    assert user_crud.create(**user_dict) is not None
    user_dict["password"] = "incorrect"
    response = client.post("/user/token", data=user_dict)
    assert response.status_code == 401
    json = response.json()
    assert json == {"detail": "Incorrect username or password"}


@pytest.mark.usefixtures("get_user_col")
def test_get_token_if_user_dont_exist(user_dict: dict[str, str]):
    response = client.post("/user/token", data=user_dict)
    assert response.status_code == 401
    json = response.json()
    assert json == {"detail": "Incorrect username or password"}


def test_create_user_if_not_exist(get_user_col: Collection, user_dict: dict[str, str]):
    assert get_user_col.count_documents({}) == 0
    response = client.post("/user/", json=user_dict)
    assert response.status_code == 201
    json = response.json()
    assert json == {"data": "OK"}
    assert get_user_col.count_documents({}) == 1


def test_create_user_if_exist(
    user_crud: User, get_user_col: Collection, user_dict: dict[str, str]
):
    assert user_crud.create(**user_dict) is not None
    assert get_user_col.count_documents({}) == 1
    response = client.post("/user/", json=user_dict)
    assert response.status_code == 200
    json = response.json()
    assert json == {"error": "User alredy exists."}
    assert get_user_col.count_documents({}) == 1


@pytest.mark.usefixtures("get_user_col")
def test_get_me_with_correct_credit(
    get_auth_header: dict[str, str], user_dict: dict[str, str]
):
    response = client.get("/user/", headers=get_auth_header)
    assert response.status_code == 200
    assert response.json() == {"data": user_dict["username"]}


@pytest.mark.usefixtures("get_user_col")
def test_get_me_with_incorrect_credit():
    response = client.get("/user/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
