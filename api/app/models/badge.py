from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Text
from sqlalchemy.orm import relationship
from ..database import Base


class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    icon = Column(String(10), default="🏅")
    description = Column(Text, default="")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", backref="badges")
    student_badges = relationship("StudentBadge", back_populates="badge", cascade="all, delete-orphan")


class StudentBadge(Base):
    __tablename__ = "student_badges"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False)
    awarded_at = Column(DateTime(timezone=True), server_default=func.now())
    awarded_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    student = relationship("Student", back_populates="badges")
    badge = relationship("Badge", back_populates="student_badges")
