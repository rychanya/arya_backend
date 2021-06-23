from pydantic import BaseModel, Field
from bson import ObjectId
from arya_backend.models.qa import QA, StrObjectId

class UploadQA(BaseModel):
    class Config:
        use_enum_values = True
    
    type: QA.type_enum
    question: str
    title: str
    is_correct: bool
    is_processed: bool = False

class Upload(BaseModel):
    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: lambda v: str(v)}

    id: StrObjectId = Field(None, alias='_id')
    data: list[UploadQA]
    by: StrObjectId