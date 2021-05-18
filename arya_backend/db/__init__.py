from arya_backend.models.auth import UserInDB
from pymongo import MongoClient

from arya_backend.config import MONGO_PASSWORD, MONGO_USER, MONGO_DB_NAME
client = MongoClient(f'mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@cluster0.ys89g.mongodb.net/{MONGO_DB_NAME}?retryWrites=true&w=majority')

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


def get_user(username: str):
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)


def create_user(username: str, password: str):
    if username not in fake_users_db:
        fake_users_db[username] = {
            "username": username,
            "hashed_password": password,
        }
        print(fake_users_db)
        return get_user(username)
