from pydantic import BaseModel
from typing import Optional

class SubjectBase(BaseModel):
    name: str
    code: Optional[str] = None

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(SubjectBase):
    pass

class SubjectInDBBase(SubjectBase):
    id: str

    class Config:
        from_attributes = True

class Subject(SubjectInDBBase):
    pass