from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta, timezone
from ..database import get_db
from ..models.student import Student
from ..models.class_ import Class
from ..models.points_log import PointsLog
from ..utils.deps import get_current_user
from ..models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/api/leaderboard", tags=["排行榜"])


class LeaderboardEntry(BaseModel):
    rank: int
    student_id: int
    student_no: str
    name: str
    pet_type: str
    level: int
    points: int
    week_points: int = 0

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    total_students: int = 0
    total_points: int = 0
    avg_points: float = 0.0
    today_records: int = 0


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    class_id: int = Query(..., description="班级ID"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cls_result = await db.execute(select(Class).where(Class.id == class_id, Class.owner_id == user.id))
    if not cls_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="无权访问")

    # 学生总数
    count_r = await db.execute(select(func.count(Student.id)).where(Student.class_id == class_id))
    total = count_r.scalar() or 0

    # 总积分
    sum_r = await db.execute(select(func.coalesce(func.sum(Student.points), 0)).where(Student.class_id == class_id))
    total_pts = sum_r.scalar() or 0

    # 今日记录数
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_r = await db.execute(
        select(func.count(PointsLog.id))
        .join(Student, PointsLog.student_id == Student.id)
        .where(Student.class_id == class_id, PointsLog.created_at >= today_start)
    )
    today_count = today_r.scalar() or 0

    return DashboardStats(
        total_students=total,
        total_points=total_pts,
        avg_points=round(total_pts / total, 1) if total > 0 else 0.0,
        today_records=today_count,
    )


@router.get("/points", response_model=list[LeaderboardEntry])
async def points_leaderboard(
    class_id: int = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cls_result = await db.execute(select(Class).where(Class.id == class_id, Class.owner_id == user.id))
    if not cls_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="无权访问")

    result = await db.execute(
        select(Student).where(Student.class_id == class_id).order_by(desc(Student.points)).limit(50)
    )
    students = result.scalars().all()

    # 计算本周积分
    week_start = datetime.now(timezone.utc) - timedelta(days=datetime.now(timezone.utc).weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    entries = []
    for i, s in enumerate(students):
        week_r = await db.execute(
            select(func.coalesce(func.sum(PointsLog.points), 0))
            .where(PointsLog.student_id == s.id, PointsLog.created_at >= week_start)
        )
        week_pts = week_r.scalar() or 0
        entries.append(LeaderboardEntry(
            rank=i + 1,
            student_id=s.id,
            student_no=s.student_no,
            name=s.name,
            pet_type=s.pet_type,
            level=s.level,
            points=s.points,
            week_points=week_pts,
        ))
    return entries


@router.get("/week", response_model=list[LeaderboardEntry])
async def week_leaderboard(
    class_id: int = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cls_result = await db.execute(select(Class).where(Class.id == class_id, Class.owner_id == user.id))
    if not cls_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="无权访问")

    week_start = datetime.now(timezone.utc) - timedelta(days=datetime.now(timezone.utc).weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    # 查询本周积分排名
    result = await db.execute(
        select(
            Student.id,
            Student.student_no,
            Student.name,
            Student.pet_type,
            Student.level,
            Student.points,
            func.coalesce(func.sum(PointsLog.points), 0).label("week_pts"),
        )
        .outerjoin(PointsLog, (PointsLog.student_id == Student.id) & (PointsLog.created_at >= week_start))
        .where(Student.class_id == class_id)
        .group_by(Student.id)
        .order_by(desc("week_pts"))
        .limit(50)
    )

    entries = []
    for i, row in enumerate(result.all()):
        entries.append(LeaderboardEntry(
            rank=i + 1,
            student_id=row.id,
            student_no=row.student_no,
            name=row.name,
            pet_type=row.pet_type,
            level=row.level,
            points=row.points,
            week_points=row.week_pts,
        ))
    return entries
