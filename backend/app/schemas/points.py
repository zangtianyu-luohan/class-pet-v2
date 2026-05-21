from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
from ..utils.sanitize import sanitize_text


class PointsAdjust(BaseModel):
    student_id: int
    points: int = Field(..., ge=-1000, le=1000, description="正数加分，负数减分")
    reason: str = Field(..., min_length=1, max_length=200)
    category: str = "manual"

    @field_validator("reason")
    @classmethod
    def sanitize(cls, v):
        return sanitize_text(v)


class PointsBatchAdjust(BaseModel):
    student_ids: List[int]
    points: int
    reason: str
    category: str = "manual"


class PointsRuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    points: int
    category: str = "bonus"
    icon: str = "⭐"


class PointsRuleUpdate(BaseModel):
    name: Optional[str] = None
    points: Optional[int] = None
    category: Optional[str] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None


class PointsLogOut(BaseModel):
    id: int
    student_id: int
    student_name: str = ""
    points: int
    reason: str
    category: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PointsRuleOut(BaseModel):
    id: int
    name: str
    points: int
    category: str
    icon: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
