from bson.objectid import ObjectId
from fastapi import APIRouter, BackgroundTasks, Depends, Security

from arya_backend.db.upload_QA import UploadCRUD
from arya_backend.dependencies import get_current_user
from arya_backend.models.auth import User
from arya_backend.models.upload_QA import Payload, Upload
from arya_backend.parser import parse

router = APIRouter(prefix="/uploads", tags=["Upload"])


@router.post("/")
async def upload(
    bt: BackgroundTasks,
    payload: list[Payload],
    user: User = Security(get_current_user, scopes=["qa:add"]),
    db: UploadCRUD = Depends(),
):
    upload_id = db.create(user.id, payload)
    bt.add_task(parse, upload_id)
    return str(upload_id)


@router.get("/{id}", response_model=Upload)
def get_uplod_by_id(
    id: str,
    user: User = Security(get_current_user, scopes=["qa:add"]),
    db: UploadCRUD = Depends(),
):
    upload = db.get_by_id(ObjectId(id))
    if upload and upload.by == user.id:
        return upload


@router.get("/")
def get(
    user: User = Security(get_current_user, scopes=["qa:add"]),
    db: UploadCRUD = Depends(),
):
    upload = db.get_by_user(user.id)
    return upload
