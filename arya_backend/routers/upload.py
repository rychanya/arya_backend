from bson.objectid import ObjectId
from fastapi import APIRouter, BackgroundTasks, Security

from arya_backend.db import upload_QA
from arya_backend.dependencies import get_current_user
from arya_backend.models.auth import User
from arya_backend.models.upload_QA import Payload, Upload
from arya_backend.parser import parse

router = APIRouter(prefix="/uploads")


@router.post("/")
async def upload(
    bt: BackgroundTasks,
    payload: list[Payload],
    user: User = Security(get_current_user, scopes=["qa:add"]),
):
    upload_id = upload_QA.create(user.id)
    bt.add_task(parse, upload_id, user.id, payload)
    return str(upload_id)


@router.get("/{id}")
def get_uplod_by_id(
    id: str, user: User = Security(get_current_user, scopes=["qa:add"])
):
    doc = upload_QA.get_by_id(ObjectId(id))
    if doc and doc["by"] == user.id:
        return Upload(**doc)


@router.get("/")
def get(user: User = Security(get_current_user, scopes=["qa:add"])):
    upload = upload_QA.get_by_user(user.id)
    return upload
