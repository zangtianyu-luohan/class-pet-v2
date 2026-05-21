import re
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from ..utils.sanitize import sanitize_text


def _validate_password_strength(v: str) -> str:
    """密码强度校验：至少8位，包含大小写字母和数字"""
    if len(v) < 8:
        raise ValueError("密码长度至少8位")
    if not re.search(r"[a-z]", v):
        raise ValueError("密码必须包含小写字母")
    if not re.search(r"[A-Z]", v):
        raise ValueError("密码必须包含大写字母")
    if not re.search(r"\d", v):
        raise ValueError("密码必须包含数字")
    return v


# ===== 请求 =====
class UserRegister(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=100)

    @field_validator("password")
    @classmethod
    def check_password_strength(cls, v):
        return _validate_password_strength(v)

    @field_validator("username", "display_name")
    @classmethod
    def sanitize_user_input(cls, v):
        return sanitize_text(v)


class UserLogin(BaseModel):
    username: str
    password: str
    captcha_id: Optional[str] = None
    captcha_answer: Optional[str] = None


class UserUpdate(BaseModel):
    display_name: Optional[str] = None


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def check_password_strength(cls, v):
        return _validate_password_strength(v)


# ===== 响应 =====
class UserOut(BaseModel):
    id: int
    username: str
    display_name: str
    is_admin: bool = False
    expires_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
