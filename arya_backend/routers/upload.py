from bson.objectid import ObjectId
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Request,
    Security,
    UploadFile,
)
from pydantic import BaseModel

from arya_backend.db import QA, fs, upload_QA
from arya_backend.dependencies import get_current_user
from arya_backend.models.auth import User
from arya_backend.models.upload_QA import Payload, Upload
from arya_backend.parser import parse

router = APIRouter(prefix="/uploads")


# @router.get("/")
# def get_uploads(user: User = Depends(get_current_user)):
#     return upload_QA.get_all(user)


# @router.get("/file/{id}")
# def dowload_file(id: str, user: User = Depends(get_current_user)):
#     try:
#         _id = ObjectId(id)
#         file = fs.get(_id)
#         return StreamingResponse(
#             BytesIO(file.read()),
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         )
#     except (InvalidId, TypeError):
#         return


# @router.get("/{id}")
# def get_upload(
#     id: str,
#     user: User = Depends(get_current_user),
# ):
#     payload = upload_QA.get(id)
#     if payload and payload.by == user.id:
#         return payload


@router.post("/")
async def upload(
    # bt: BackgroundTasks,
    # file: UploadFile = File(...),
    payload: list[Payload],
    user: User = Security(get_current_user, scopes=["qa:add"]),
):
    # file_id = fs.put(file.file, metadata={"by": user.id})
    # bt.add_task(parse, file_id)
    # return str(file_id)
    return [el.dict() for el in payload]


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
