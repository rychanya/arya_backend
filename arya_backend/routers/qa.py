from fastapi import APIRouter

from arya_backend.db import QA

router = APIRouter(prefix="/qa")


@router.get("/search")
def search(q: str):
    res = QA.search(q)
    print(res)
    return res
