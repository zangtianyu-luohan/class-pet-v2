from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Text, Boolean
from sqlalchemy.orm import relationship
from ..database import Base


class PointsLog(Base):
    __tablename__ = "points_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    points = Column(Integer, nullable=False)  # 正数加分，负数减分
    reason = Column(String(200), nullable=False)
    category = Column(String(50), default="manual")  # manual/bonus/penalty/tool
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="points_logs")
    operator = relationship("User", backref="points_logs")


class PointsRule(Base):
    __tablename__ = "points_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    points = Column(Integer, nullable=False)
    category = Column(String(50), default="bonus")  # bonus/penalty
    icon = Column(String(10), default="⭐")
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", backref="points_rules")
