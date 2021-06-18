from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File

from arya_backend.db import QA
from arya_backend.parser import parse_xl

router = APIRouter(prefix="/qa")


@router.get("/search")
def search(q: str, page: int = 1) -> Optional[list]:
    return list(QA.search(q, page))


@router.get("/{id}")
def get(id: str):
    doc = QA.get(id)
    if doc is None:
        raise HTTPException(404)
    return doc

@router.post("/upload")
def upload(file: UploadFile = File(...)):
    return parse_xl(file.file.read())