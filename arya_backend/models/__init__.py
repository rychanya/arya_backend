from typing import Optional

from pydantic import BaseModel


class MessageModel(BaseModel):
    error: Optional[str]
    data: Optional[str]
