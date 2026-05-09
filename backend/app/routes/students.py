import csv
import io
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from ..database import get_db
from ..models.student import Student
from ..models.class_ import Class
from ..models.points_log import PointsLog
from ..schemas.student import StudentCreate, StudentBatchCreate, StudentUpdate, StudentOut
from ..schemas.points import PointsAdjust, PointsBatchAdjust, PointsLogOut
from ..utils.deps import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/students", tags=["学生管理"])


# 等级经验值表
LEVEL_EXP = [0, 100, 300, 600, 1000, 1500, 2100, 2800, 3600, 4500, 5500]


def calc_level(points: int) -> tuple[int, float]:
    level = 1
    for i, exp in enumerate(LEVEL_EXP):
        if points >= exp:
            level = i + 1
        else:
            break
    return level, points


@router.get("/", response_model=list[StudentOut])
async def list_students(
    class_id: int = Query(..., description="班级ID"),
    search: str = Query("", description="搜索关键词"),
    sort_by: str = Query("points", description="排序字段"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 验证班级归属
    cls_result = await db.execute(select(Class).where(Class.id == class_id, Class.owner_id == user.id))
    if not cls_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="无权访问此班级")

    query = select(Student).where(Student.class_id == class_id)
    if search:
        query = query.where(or_(Student.name.contains(search), Student.student_no.contains(search)))

    if sort_by == "name":
        query = query.order_by(Student.name)
    elif sort_by == "level":
        query = query.order_by(Student.level.desc(), Student.points.desc())
    else:
        query = query.order_by(Student.points.desc())

    result = await db.execute(query)
    return [StudentOut.model_validate(s) for s in result.scalars().all()]


@router.post("/", response_model=StudentOut)
async def create_student(
    class_id: int,
    data: StudentCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 验证班级归属
    cls_result = await db.execute(select(Class).where(Class.id == class_id, Class.owner_id == user.id))
    if not cls_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="无权访问此班级")

    # 检查学号是否重复
    exists = await db.execute(
        select(Student).where(Student.class_id == class_id, Student.student_no == data.student_no)
    )
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"学号 {data.student_no} 已存在")

    student = Student(
        student_no=data.student_no,
        name=data.name,
        pet_type=data.pet_type,
        pet_name=data.pet_name,
        class_id=class_id,
    )
    db.add(student)
    await db.flush()
    await db.refresh(student)
    return StudentOut.model_validate(student)


@router.post("/batch", response_model=list[StudentOut])
async def batch_create_students(
    class_id: int,
    data: StudentBatchCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cls_result = await db.execute(select(Class).where(Class.id == class_id, Class.owner_id == user.id))
    if not cls_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="无权访问此班级")

    created = []
    for s in data.students:
        exists = await db.execute(
            select(Student).where(Student.class_id == class_id, Student.student_no == s.student_no)
        )
        if exists.scalar_one_or_none():
            continue
        student = Student(
            student_no=s.student_no,
            name=s.name,
            pet_type=s.pet_type,
            pet_name=s.pet_name,
            class_id=class_id,
        )
        db.add(student)
        await db.flush()
        await db.refresh(student)
        created.append(StudentOut.model_validate(student))
    return created


@router.get("/{student_id}", response_model=StudentOut)
async def get_student(
    student_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    # 验证班级归属
    cls_result = await db.execute(select(Class).where(Class.id == student.class_id, Class.owner_id == user.id))
    if not cls_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="无权访问此学生")

    return StudentOut.model_validate(student)


@router.put("/{student_id}", response_model=StudentOut)
async def update_student(
    student_id: int,
    data: StudentUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    cls_result = await db.execute(select(Class).where(Class.id == student.class_id, Class.owner_id == user.id))
    if not cls_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="无权操作")

    if data.name is not None:
        student.name = data.name
    if data.student_no is not None:
        student.student_no = data.student_no
    if data.pet_type is not None:
        student.pet_type = data.pet_type
    if data.pet_name is not None:
        student.pet_name = data.pet_name

    await db.flush()
    await db.refresh(student)
    return StudentOut.model_validate(student)


@router.delete("/{student_id}")
async def delete_student(
    student_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    cls_result = await db.execute(select(Class).where(Class.id == student.class_id, Class.owner_id == user.id))
    if not cls_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="无权操作")

    await db.delete(student)
    return {"message": "学生已删除"}


# ===== 积分操作 =====
@router.post("/points/adjust", response_model=PointsLogOut)
async def adjust_points(
    data: PointsAdjust,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Student).where(Student.id == data.student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    # 验证班级归属
    cls_result = await db.execute(select(Class).where(Class.id == student.class_id, Class.owner_id == user.id))
    if not cls_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="无权操作")

    student.points += data.points
    student.level, student.experience = calc_level(student.points)

    log = PointsLog(
        student_id=data.student_id,
        points=data.points,
        reason=data.reason,
        category=data.category,
        operator_id=user.id,
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)

    out = PointsLogOut.model_validate(log)
    out.student_name = student.name
    return out


@router.post("/points/batch", response_model=list[PointsLogOut])
async def batch_adjust_points(
    data: PointsBatchAdjust,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    logs = []
    for sid in data.student_ids:
        result = await db.execute(select(Student).where(Student.id == sid))
        student = result.scalar_one_or_none()
        if not student:
            continue

        cls_result = await db.execute(select(Class).where(Class.id == student.class_id, Class.owner_id == user.id))
        if not cls_result.scalar_one_or_none():
            continue

        student.points += data.points
        student.level, student.experience = calc_level(student.points)

        log = PointsLog(
            student_id=sid,
            points=data.points,
            reason=data.reason,
            category=data.category,
            operator_id=user.id,
        )
        db.add(log)
        await db.flush()
        await db.refresh(log)

        out = PointsLogOut.model_validate(log)
        out.student_name = student.name
        logs.append(out)
    return logs


@router.get("/{student_id}/logs", response_model=list[PointsLogOut])
async def get_student_logs(
    student_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PointsLog)
        .where(PointsLog.student_id == student_id)
        .order_by(PointsLog.created_at.desc())
        .limit(50)
    )
    logs = result.scalars().all()

    out = []
    for log in logs:
        student_result = await db.execute(select(Student).where(Student.id == log.student_id))
        student = student_result.scalar_one_or_none()
        o = PointsLogOut.model_validate(log)
        o.student_name = student.name if student else "未知"
        out.append(o)
    return out


# ===== CSV 导出 =====
@router.get("/export")
async def export_students_csv(
    class_id: int = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cls_result = await db.execute(select(Class).where(Class.id == class_id, Class.owner_id == user.id))
    cls = cls_result.scalar_one_or_none()
    if not cls:
        raise HTTPException(status_code=403, detail="无权访问")

    result = await db.execute(
        select(Student).where(Student.class_id == class_id).order_by(Student.points.desc())
    )
    students = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["序号", "学号", "姓名", "萌宠类型", "萌宠昵称", "等级", "积分"])
    for i, s in enumerate(students):
        writer.writerow([i + 1, s.student_no, s.name, s.pet_type, s.pet_name, s.level, s.points])

    output.seek(0)
    # 添加 BOM 以便 Excel 正确识别中文
    bom_output = io.BytesIO()
    bom_output.write(b'\xef\xbb\xbf')
    bom_output.write(output.getvalue().encode('utf-8'))
    bom_output.seek(0)

    filename = f"{cls.name}_学生数据.csv"
    return StreamingResponse(
        bom_output,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )
