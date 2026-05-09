from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# ===== 请求 =====
class UserRegister(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=4, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    avatar: Optional[str] = None


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=4, max_length=100)


# ===== 响应 =====
class UserOut(BaseModel):
    id: int
    username: str
    display_name: str
    avatar: str = ""
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
