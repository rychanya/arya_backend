from typing import Optional

from fastapi import APIRouter, HTTPException

from arya_backend.db import QA

router = APIRouter(prefix="/qa")


@router.get("/search")
def search2(q: str) -> Optional[list]:
    return list(QA.searc_inc(q))


# @router.get("/search")
# def search(q: str, page: int = 1) -> Optional[list]:
#     return list(QA.search(q, page))


@router.get("/inc/{id}")
def get_inc(id: str):
    doc = QA.get_inc(id)
    if doc is None:
        raise HTTPException(404)
    return doc


@router.get("/{id}")
def get(id: str):
    doc = QA.get(id)
    if doc is None:
        raise HTTPException(404)
    return doc
