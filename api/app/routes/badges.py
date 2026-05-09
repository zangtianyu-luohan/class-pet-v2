from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models.badge import Badge, StudentBadge
from ..models.student import Student
from ..models.class_ import Class
from ..schemas.badge import BadgeCreate, BadgeUpdate, BadgeOut, StudentBadgeCreate, StudentBadgeOut
from ..utils.deps import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/badges", tags=["勋章管理"])


@router.get("/", response_model=list[BadgeOut])
async def list_badges(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Badge).where(Badge.owner_id == user.id))
    return [BadgeOut.model_validate(b) for b in result.scalars().all()]


@router.post("/", response_model=BadgeOut)
async def create_badge(
    data: BadgeCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    badge = Badge(name=data.name, icon=data.icon, description=data.description, owner_id=user.id)
    db.add(badge)
    await db.flush()
    await db.refresh(badge)
    return BadgeOut.model_validate(badge)


@router.put("/{badge_id}", response_model=BadgeOut)
async def update_badge(
    badge_id: int,
    data: BadgeUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Badge).where(Badge.id == badge_id, Badge.owner_id == user.id))
    badge = result.scalar_one_or_none()
    if not badge:
        raise HTTPException(status_code=404, detail="勋章不存在")

    if data.name is not None:
        badge.name = data.name
    if data.icon is not None:
        badge.icon = data.icon
    if data.description is not None:
        badge.description = data.description
    await db.flush()
    await db.refresh(badge)
    return BadgeOut.model_validate(badge)


@router.delete("/{badge_id}")
async def delete_badge(
    badge_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Badge).where(Badge.id == badge_id, Badge.owner_id == user.id))
    badge = result.scalar_one_or_none()
    if not badge:
        raise HTTPException(status_code=404, detail="勋章不存在")
    await db.delete(badge)
    return {"message": "勋章已删除"}


# ===== 颁发勋章 =====
@router.post("/award", response_model=StudentBadgeOut)
async def award_badge(
    data: StudentBadgeCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 验证勋章归属
    badge_result = await db.execute(select(Badge).where(Badge.id == data.badge_id, Badge.owner_id == user.id))
    badge = badge_result.scalar_one_or_none()
    if not badge:
        raise HTTPException(status_code=404, detail="勋章不存在")

    # 验证学生存在且归属
    student_result = await db.execute(select(Student).where(Student.id == data.student_id))
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    cls_result = await db.execute(select(Class).where(Class.id == student.class_id, Class.owner_id == user.id))
    if not cls_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="无权操作")

    # 检查是否已颁发
    exists = await db.execute(
        select(StudentBadge).where(
            StudentBadge.student_id == data.student_id,
            StudentBadge.badge_id == data.badge_id,
        )
    )
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该学生已获得此勋章")

    sb = StudentBadge(
        student_id=data.student_id,
        badge_id=data.badge_id,
        awarded_by=user.id,
    )
    db.add(sb)
    await db.flush()
    await db.refresh(sb)

    out = StudentBadgeOut.model_validate(sb)
    out.badge_name = badge.name
    out.badge_icon = badge.icon
    out.student_name = student.name
    return out


@router.get("/student/{student_id}", response_model=list[StudentBadgeOut])
async def get_student_badges(
    student_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StudentBadge).where(StudentBadge.student_id == student_id)
    )
    sbs = result.scalars().all()

    out = []
    for sb in sbs:
        badge_r = await db.execute(select(Badge).where(Badge.id == sb.badge_id))
        badge = badge_r.scalar_one_or_none()
        student_r = await db.execute(select(Student).where(Student.id == sb.student_id))
        student = student_r.scalar_one_or_none()
        o = StudentBadgeOut.model_validate(sb)
        o.badge_name = badge.name if badge else "未知"
        o.badge_icon = badge.icon if badge else "🏅"
        o.student_name = student.name if student else "未知"
        out.append(o)
    return out


@router.get("/records", response_model=list[StudentBadgeOut])
async def get_award_records(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户颁发的所有勋章记录"""
    result = await db.execute(
        select(StudentBadge).where(StudentBadge.awarded_by == user.id).order_by(StudentBadge.awarded_at.desc())
    )
    sbs = result.scalars().all()

    out = []
    for sb in sbs:
        badge_r = await db.execute(select(Badge).where(Badge.id == sb.badge_id))
        badge = badge_r.scalar_one_or_none()
        student_r = await db.execute(select(Student).where(Student.id == sb.student_id))
        student = student_r.scalar_one_or_none()
        o = StudentBadgeOut.model_validate(sb)
        o.badge_name = badge.name if badge else "已删除"
        o.badge_icon = badge.icon if badge else "🏅"
        o.student_name = student.name if student else "已删除"
        out.append(o)
    return out
