from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta, timezone
from ..database import get_db
from ..models.student import Student
from ..models.class_ import Class
from ..models.points_log import PointsLog
from ..utils.deps import get_current_user
from ..utils.stats import compute_class_stats, ClassStatsData
from ..models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/api/leaderboard", tags=["排行榜"])


class LeaderboardEntry(BaseModel):
    rank: int
    student_id: int
    student_no: str
    name: str
    points: int
    week_points: int = 0

    model_config = {"from_attributes": True}


@router.get("/stats", response_model=ClassStatsData)
async def get_dashboard_stats(
    class_id: int = Query(..., description="班级ID"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cls_result = await db.execute(select(Class).where(Class.id == class_id, Class.owner_id == user.id))
    if not cls_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="无权访问")

    return await compute_class_stats(db, class_id)


@router.get("/points", response_model=list[LeaderboardEntry])
async def points_leaderboard(
    class_id: int = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cls_result = await db.execute(select(Class).where(Class.id == class_id, Class.owner_id == user.id))
    if not cls_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="无权访问")

    week_start = datetime.now(timezone.utc) - timedelta(days=datetime.now(timezone.utc).weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    result = await db.execute(
        select(
            Student.id,
            Student.student_no,
            Student.name,
            Student.points,
            func.coalesce(func.sum(PointsLog.points), 0).label("week_pts"),
        )
        .outerjoin(PointsLog, (PointsLog.student_id == Student.id) & (PointsLog.created_at >= week_start))
        .where(Student.class_id == class_id)
        .group_by(Student.id)
        .order_by(desc(Student.points))
    )

    entries = []
    for i, row in enumerate(result.all()):
        entries.append(LeaderboardEntry(
            rank=i + 1,
            student_id=row.id,
            student_no=row.student_no,
            name=row.name,
            points=row.points,
            week_points=row.week_pts,
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
            Student.points,
            func.coalesce(func.sum(PointsLog.points), 0).label("week_pts"),
        )
        .outerjoin(PointsLog, (PointsLog.student_id == Student.id) & (PointsLog.created_at >= week_start))
        .where(Student.class_id == class_id)
        .group_by(Student.id)
        .order_by(desc("week_pts"))
    )

    entries = []
    for i, row in enumerate(result.all()):
        entries.append(LeaderboardEntry(
            rank=i + 1,
            student_id=row.id,
            student_no=row.student_no,
            name=row.name,
            points=row.points,
            week_points=row.week_pts,
        ))
    return entries
