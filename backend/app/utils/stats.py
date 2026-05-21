from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone
from ..models.student import Student
from ..models.points_log import PointsLog


class ClassStatsData(BaseModel):
    total_students: int = 0
    total_points: int = 0
    avg_points: float = 0.0
    today_records: int = 0


async def compute_class_stats(db: AsyncSession, class_id: int) -> ClassStatsData:
    """Compute aggregated stats for a class (shared by dashboard and class stats)."""
    count_r = await db.execute(select(func.count(Student.id)).where(Student.class_id == class_id))
    total = count_r.scalar() or 0

    sum_r = await db.execute(select(func.coalesce(func.sum(Student.points), 0)).where(Student.class_id == class_id))
    total_pts = sum_r.scalar() or 0

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_r = await db.execute(
        select(func.count(PointsLog.id))
        .join(Student, PointsLog.student_id == Student.id)
        .where(Student.class_id == class_id, PointsLog.created_at >= today_start)
    )
    today_count = today_r.scalar() or 0

    return ClassStatsData(
        total_students=total,
        total_points=total_pts,
        avg_points=round(total_pts / total, 1) if total > 0 else 0.0,
        today_records=today_count,
    )
