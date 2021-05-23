from fastapi import APIRouter

from arya_backend.db import QA

router = APIRouter(prefix="/qa")


@router.get("/search")
def search(q: str):
    return QA.search(q)
