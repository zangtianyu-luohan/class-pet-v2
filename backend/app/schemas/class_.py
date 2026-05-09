from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ClassCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""


class ClassUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ClassOut(BaseModel):
    id: int
    name: str
    description: str
    is_active: bool
    student_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}
