import csv
import io
from urllib.parse import quote
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
from ..utils.sanitize import escape_like
from ..models.user import User

router = APIRouter(prefix="/api/students", tags=["学生管理"])


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
        safe = escape_like(search)
        query = query.where(or_(Student.name.like(f"%{safe}%", escape="\\"), Student.student_no.like(f"%{safe}%", escape="\\")))

    if sort_by == "name":
        query = query.order_by(Student.name)
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
            class_id=class_id,
        )
        db.add(student)
        await db.flush()
        await db.refresh(student)
        created.append(StudentOut.model_validate(student))
    return created


@router.get("/points-logs")
async def list_points_logs(
    class_id: int = Query(..., description="班级ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=9999),
    search: str = Query("", description="搜索学生姓名或原因"),
    category: str = Query("", description="类型筛选"),
    start_date: str = Query("", description="开始日期 YYYY-MM-DD"),
    end_date: str = Query("", description="结束日期 YYYY-MM-DD"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取班级的积分日志（前端教师端用）"""
    cls_result = await db.execute(select(Class).where(Class.id == class_id, Class.owner_id == user.id))
    if not cls_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="无权访问此班级")

    # 获取班级所有学生ID
    students_result = await db.execute(select(Student.id, Student.name).where(Student.class_id == class_id))
    student_rows = students_result.all()
    student_ids = [r[0] for r in student_rows]
    student_name_map = {r[0]: r[1] for r in student_rows}
    if not student_ids:
        return {"items": [], "total": 0, "page": page, "page_size": page_size}

    # 构建查询条件
    from datetime import datetime
    base_filter = PointsLog.student_id.in_(student_ids)
    conditions = [base_filter]

    if category:
        conditions.append(PointsLog.category == category)

    if start_date:
        try:
            dt = datetime.strptime(start_date, "%Y-%m-%d")
            conditions.append(PointsLog.created_at >= dt)
        except ValueError:
            pass

    if end_date:
        try:
            dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            conditions.append(PointsLog.created_at <= dt)
        except ValueError:
            pass

    combined_filter = conditions[0]
    for c in conditions[1:]:
        combined_filter = combined_filter & c

    # 搜索：先按学生名匹配
    matched_student_ids = None
    if search:
        matched_student_ids = [sid for sid, name in student_name_map.items() if search in name]
        if not matched_student_ids:
            return {"items": [], "total": 0, "page": page, "page_size": page_size}

    # 查询日志
    count_filter = combined_filter
    logs_filter = combined_filter
    if matched_student_ids is not None:
        safe_search = escape_like(search)
        search_filter = PointsLog.student_id.in_(matched_student_ids) | PointsLog.reason.like(f"%{safe_search}%", escape="\\")
        count_filter = combined_filter & search_filter
        logs_filter = combined_filter & search_filter

    count_q = await db.execute(select(func.count(PointsLog.id)).where(count_filter))
    total = count_q.scalar()

    offset = (page - 1) * page_size
    logs_q = await db.execute(
        select(PointsLog)
        .where(logs_filter)
        .order_by(PointsLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    logs = logs_q.scalars().all()

    items = []
    for log in logs:
        items.append({
            "id": log.id,
            "student_id": log.student_id,
            "student_name": student_name_map.get(log.student_id, "未知"),
            "points": log.points,
            "reason": log.reason,
            "category": log.category or "",
            "created_at": log.created_at.isoformat() if log.created_at else "",
        })
    return {"items": items, "total": total, "page": page, "page_size": page_size}


# ===== CSV 导出（必须在 /{student_id} 之前，否则 "export" 会被当作 student_id）=====
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
    writer.writerow(["序号", "学号", "姓名", "积分"])
    for i, s in enumerate(students):
        writer.writerow([i + 1, s.student_no, s.name, s.points])

    output.seek(0)
    # 添加 BOM 以便 Excel 正确识别中文
    bom_output = io.BytesIO()
    bom_output.write(b'\xef\xbb\xbf')
    bom_output.write(output.getvalue().encode('utf-8'))
    bom_output.seek(0)

    filename = quote(f"{cls.name}_学生数据.csv")
    return StreamingResponse(
        bom_output,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )


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

    # 积分下限保护：不允许低于 -100
    if student.points + data.points < -100:
        raise HTTPException(status_code=400, detail=f"积分不能低于 -100（当前 {student.points}）")

    student.points += data.points

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
    # 批量查询所有学生（避免 N+1）
    result = await db.execute(select(Student).where(Student.id.in_(data.student_ids)))
    students_map = {s.id: s for s in result.scalars().all()}

    # 批量验证班级归属
    class_ids = {s.class_id for s in students_map.values()}
    cls_result = await db.execute(
        select(Class.id).where(Class.id.in_(class_ids), Class.owner_id == user.id)
    )
    owned_class_ids = {row[0] for row in cls_result.all()}

    logs = []
    for sid in data.student_ids:
        student = students_map.get(sid)
        if not student or student.class_id not in owned_class_ids:
            continue

        # 积分下限保护
        if student.points + data.points < -100:
            continue

        student.points += data.points

        log = PointsLog(
            student_id=sid,
            points=data.points,
            reason=data.reason,
            category=data.category,
            operator_id=user.id,
        )
        db.add(log)
        logs.append((log, student.name))

    # 统一 flush，保证事务一致性
    await db.flush()
    for log, name in logs:
        await db.refresh(log)

    result = []
    for log, name in logs:
        out = PointsLogOut.model_validate(log)
        out.student_name = name
        result.append(out)
    return result


@router.post("/points/reset")
async def reset_class_points(
    class_id: int = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """一键清零班级所有学生积分"""
    cls_result = await db.execute(select(Class).where(Class.id == class_id, Class.owner_id == user.id))
    if not cls_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="无权操作")

    result = await db.execute(select(Student).where(Student.class_id == class_id))
    students = result.scalars().all()
    count = 0
    for s in students:
        if s.points != 0:
            # 记录清零日志
            log = PointsLog(
                student_id=s.id,
                points=-s.points,
                reason="学期积分清零",
                category="reset",
                operator_id=user.id,
            )
            db.add(log)
            s.points = 0
            count += 1

    await db.flush()
    return {"message": f"已清零 {count} 名学生的积分"}


@router.post("/points/undo")
async def undo_last_points(
    class_id: int = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """撤销当前用户在该班级的最后一条积分操作"""
    cls_result = await db.execute(select(Class).where(Class.id == class_id, Class.owner_id == user.id))
    if not cls_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="无权操作")

    # 获取班级所有学生 ID
    students_result = await db.execute(select(Student.id).where(Student.class_id == class_id))
    student_ids = [row[0] for row in students_result.all()]
    if not student_ids:
        raise HTTPException(status_code=400, detail="班级没有学生")

    # 查找当前用户的最后一条操作
    log_result = await db.execute(
        select(PointsLog)
        .where(PointsLog.student_id.in_(student_ids), PointsLog.operator_id == user.id)
        .order_by(PointsLog.created_at.desc())
        .limit(1)
    )
    last_log = log_result.scalar_one_or_none()
    if not last_log:
        raise HTTPException(status_code=400, detail="没有可撤销的操作")

    # 撤销：反向操作
    student_result = await db.execute(select(Student).where(Student.id == last_log.student_id))
    student = student_result.scalar_one_or_none()
    if student:
        student.points -= last_log.points

    # 记录撤销日志
    undo_log = PointsLog(
        student_id=last_log.student_id,
        points=-last_log.points,
        reason=f"撤销：{last_log.reason}",
        category="undo",
        operator_id=user.id,
    )
    db.add(undo_log)
    await db.flush()

    return {"message": f"已撤销对 {student.name} 的 {last_log.points:+d} 积分（{last_log.reason}）"}


@router.get("/{student_id}/logs", response_model=list[PointsLogOut])
async def get_student_logs(
    student_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 先查询学生信息（单次查询）
    student_result = await db.execute(select(Student).where(Student.id == student_id))
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    # 验证班级归属
    cls_result = await db.execute(select(Class).where(Class.id == student.class_id, Class.owner_id == user.id))
    if not cls_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="无权访问")

    result = await db.execute(
        select(PointsLog)
        .where(PointsLog.student_id == student_id)
        .order_by(PointsLog.created_at.desc())
        .limit(50)
    )
    logs = result.scalars().all()

    out = []
    for log in logs:
        o = PointsLogOut.model_validate(log)
        o.student_name = student.name
        out.append(o)
    return out
