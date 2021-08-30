from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from arya_backend.db.QA import QACRUD
from arya_backend.dependencies import id_parser

router = APIRouter(prefix="/qa", tags=["QA"])


@router.get("/search")
def search2(q: str) -> Optional[list]:
    # return list(QA.searc_inc(q))
    return ["todo"]


@router.get("/{id}")
def get(_id: Optional[ObjectId] = Depends(id_parser), db: QACRUD = Depends()):
    if _id is None:
        raise HTTPException(404)
    doc = db.get(_id)
    if doc is None:
        raise HTTPException(404)
    return doc
