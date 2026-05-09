from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class BadgeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    icon: str = "🏅"
    description: str = ""


class BadgeUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None


class BadgeOut(BaseModel):
    id: int
    name: str
    icon: str
    description: str
    created_at: datetime

    model_config = {"from_attributes": True}


class StudentBadgeCreate(BaseModel):
    student_id: int
    badge_id: int


class StudentBadgeOut(BaseModel):
    id: int
    student_id: int
    badge_id: int
    badge_name: str = ""
    badge_icon: str = ""
    student_name: str = ""
    awarded_at: datetime

    model_config = {"from_attributes": True}
