from pydantic import BaseModel


class ErrorModel(BaseModel):
    error: str


class SucsesModel(BaseModel):
    message: str
