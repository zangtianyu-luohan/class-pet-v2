from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..database import get_db
from ..models.class_ import Class
from ..models.student import Student
from ..schemas.class_ import ClassCreate, ClassUpdate, ClassOut
from ..utils.deps import get_current_user
from ..utils.stats import compute_class_stats, ClassStatsData
from ..models.user import User

router = APIRouter(prefix="/api/classes", tags=["班级管理"])


@router.get("/", response_model=list[ClassOut])
async def list_classes(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Class, func.count(Student.id).label("student_count"))
        .outerjoin(Student, Student.class_id == Class.id)
        .where(Class.owner_id == user.id, Class.is_active == True)
        .group_by(Class.id)
    )

    out = []
    for cls, count in result.all():
        obj = ClassOut.model_validate(cls)
        obj.student_count = count
        out.append(obj)
    return out


@router.post("/", response_model=ClassOut)
async def create_class(
    data: ClassCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cls = Class(name=data.name, description=data.description, owner_id=user.id)
    db.add(cls)
    await db.flush()
    await db.refresh(cls)
    obj = ClassOut.model_validate(cls)
    obj.student_count = 0
    return obj


@router.put("/{class_id}", response_model=ClassOut)
async def update_class(
    class_id: int,
    data: ClassUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Class).where(Class.id == class_id, Class.owner_id == user.id))
    cls = result.scalar_one_or_none()
    if not cls:
        raise HTTPException(status_code=404, detail="班级不存在")

    if data.name is not None:
        cls.name = data.name
    if data.description is not None:
        cls.description = data.description
    await db.flush()
    await db.refresh(cls)

    count_result = await db.execute(select(func.count(Student.id)).where(Student.class_id == cls.id))
    obj = ClassOut.model_validate(cls)
    obj.student_count = count_result.scalar() or 0
    return obj


@router.delete("/{class_id}")
async def delete_class(
    class_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Class).where(Class.id == class_id, Class.owner_id == user.id))
    cls = result.scalar_one_or_none()
    if not cls:
        raise HTTPException(status_code=404, detail="班级不存在")

    cls.is_active = False
    await db.flush()
    return {"message": "班级已删除"}


@router.get("/{class_id}/stats", response_model=ClassStatsData)
async def get_class_stats(
    class_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cls_result = await db.execute(select(Class).where(Class.id == class_id, Class.owner_id == user.id))
    if not cls_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="无权访问")

    return await compute_class_stats(db, class_id)
