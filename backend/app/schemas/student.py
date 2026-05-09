from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class StudentCreate(BaseModel):
    student_no: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    pet_type: str = "cat"
    pet_name: str = ""


class StudentBatchCreate(BaseModel):
    students: List[StudentCreate]


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    student_no: Optional[str] = None
    pet_type: Optional[str] = None
    pet_name: Optional[str] = None


class StudentOut(BaseModel):
    id: int
    student_no: str
    name: str
    avatar: str = ""
    pet_type: str
    pet_name: str
    points: int
    level: int
    experience: float
    class_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class StudentBrief(BaseModel):
    id: int
    student_no: str
    name: str
    pet_type: str
    points: int
    level: int

    model_config = {"from_attributes": True}
