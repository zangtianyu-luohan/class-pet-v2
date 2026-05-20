from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    display_name = Column(String(100), nullable=False)
    is_admin = Column(Boolean, default=False, comment="是否管理员")
    avatar = Column(String(255), default="")
    expires_at = Column(DateTime(timezone=True), nullable=True, comment="账号有效期，null表示永久")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
