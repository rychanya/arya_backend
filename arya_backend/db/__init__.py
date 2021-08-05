import certifi
from pymongo import MongoClient

from arya_backend.config import MONGO_DB_NAME, MONGO_PASSWORD, MONGO_USER

client = MongoClient(
    f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@cluster0.ys89g.mongodb.net/{MONGO_DB_NAME}?retryWrites=true&w=majority",
    tlsCAFile=certifi.where(),
)
