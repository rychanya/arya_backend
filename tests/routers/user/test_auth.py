import pytest
from fastapi.testclient import TestClient

from arya_backend.auth import decode_access_token
from arya_backend.db.user import User
from arya_backend.main import app

client = TestClient(app)


@pytest.mark.usefixtures("get_user_col")
def test_get_token_with_correct_credit(user_crud: User, user_dict: dict[str, str]):
    assert user_crud.create(**user_dict) is not None
    responce = client.post("/user/token", data=user_dict)
    assert responce.status_code == 200
    json = responce.json()
    assert json["token_type"] == "bearer"
    token = json["access_token"]
    token_data = decode_access_token(token)
    assert token_data.username == user_dict["username"]


@pytest.mark.usefixtures("get_user_col")
def test_get_token_with_incorrect_credit(user_crud: User, user_dict: dict[str, str]):
    assert user_crud.create(**user_dict) is not None
    user_dict["password"] = "incorrect"
    responce = client.post("/user/token", data=user_dict)
    assert responce.status_code == 401
    json = responce.json()
    assert json == {"detail": "Incorrect username or password"}


@pytest.mark.usefixtures("get_user_col")
def test_get_token_if_user_dont_exist(user_dict: dict[str, str]):
    responce = client.post("/user/token", data=user_dict)
    assert responce.status_code == 401
    json = responce.json()
    assert json == {"detail": "Incorrect username or password"}
