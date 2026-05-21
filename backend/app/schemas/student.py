from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
from ..utils.sanitize import sanitize_text


class StudentCreate(BaseModel):
    student_no: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)

    @field_validator("name", "student_no")
    @classmethod
    def sanitize(cls, v):
        return sanitize_text(v)


class StudentBatchCreate(BaseModel):
    students: List[StudentCreate]


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    student_no: Optional[str] = None


class StudentOut(BaseModel):
    id: int
    student_no: str
    name: str
    points: int
    class_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class StudentBrief(BaseModel):
    id: int
    student_no: str
    name: str
    points: int

    model_config = {"from_attributes": True}
