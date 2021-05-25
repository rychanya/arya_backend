from typing import Optional

from fastapi import APIRouter, HTTPException

from arya_backend.db import QA

router = APIRouter(prefix="/qa")


@router.get("/search")
def search(q: str) -> Optional[list]:
    return QA.search(q)

@router.get("/{id}")
def get(id: str):
    doc = QA.get(id)
    if doc is None:
        raise HTTPException(404)
    return doc
