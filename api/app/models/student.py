from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Float
from sqlalchemy.orm import relationship
from ..database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_no = Column(String(50), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    avatar = Column(String(255), default="")
    pet_type = Column(String(20), default="cat")  # cat/dog/rabbit/panda/penguin
    pet_name = Column(String(50), default="")
    points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    experience = Column(Float, default=0.0)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    class_ = relationship("Class", back_populates="students")
    points_logs = relationship("PointsLog", back_populates="student", cascade="all, delete-orphan")
    badges = relationship("StudentBadge", back_populates="student", cascade="all, delete-orphan")
