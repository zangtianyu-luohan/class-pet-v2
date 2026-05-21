"""
管理后台路由
- 系统统计概览
- 用户管理
- 登录日志
- 操作日志
- 数据库可视化CRUD
"""
import platform
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, text, inspect as sa_inspect
from ..config import settings
from ..database import get_db, engine
from ..models.user import User
from ..models.class_ import Class
from ..models.student import Student
from ..models.points_log import PointsLog, PointsRule
from ..models.badge import Badge, StudentBadge
from ..utils.deps import get_current_user
from ..utils.auth import hash_password
from ..utils.login_security import LoginLog

# 表名 -> 模型映射
TABLE_MODELS = {
    "users": User,
    "classes": Class,
    "students": Student,
    "points_logs": PointsLog,
    "points_rules": PointsRule,
    "badges": Badge,
    "student_badges": StudentBadge,
    "login_logs": LoginLog,
}

# 每张表的列定义
TABLE_COLUMNS = {
    "users": [
        {"key": "id", "label": "ID", "type": "int", "editable": False, "required": False},
        {"key": "username", "label": "用户名", "type": "str", "editable": True, "required": True},
        {"key": "display_name", "label": "显示名称", "type": "str", "editable": True, "required": True},
        {"key": "is_admin", "label": "管理员", "type": "bool", "editable": True, "required": False},
        {"key": "expires_at", "label": "有效期", "type": "datetime", "editable": True, "required": False, "comment": "留空表示永久"},
        {"key": "created_at", "label": "创建时间", "type": "datetime", "editable": False, "required": False},
    ],
    "classes": [
        {"key": "id", "label": "ID", "type": "int", "editable": False, "required": False},
        {"key": "name", "label": "班级名称", "type": "str", "editable": True, "required": True},
        {"key": "description", "label": "描述", "type": "str", "editable": True, "required": False},
        {"key": "owner_id", "label": "所属用户ID", "type": "int", "editable": True, "required": True},
        {"key": "is_active", "label": "启用", "type": "bool", "editable": True, "required": False},
        {"key": "created_at", "label": "创建时间", "type": "datetime", "editable": False, "required": False},
    ],
    "students": [
        {"key": "id", "label": "ID", "type": "int", "editable": False, "required": False},
        {"key": "student_no", "label": "学号", "type": "str", "editable": True, "required": True},
        {"key": "name", "label": "姓名", "type": "str", "editable": True, "required": True},
        {"key": "points", "label": "积分", "type": "int", "editable": True, "required": False},
        {"key": "class_id", "label": "班级ID", "type": "int", "editable": True, "required": True},
        {"key": "created_at", "label": "创建时间", "type": "datetime", "editable": False, "required": False},
    ],
    "points_logs": [
        {"key": "id", "label": "ID", "type": "int", "editable": False, "required": False},
        {"key": "student_id", "label": "学生ID", "type": "int", "editable": True, "required": True},
        {"key": "points", "label": "积分", "type": "int", "editable": True, "required": True},
        {"key": "reason", "label": "原因", "type": "str", "editable": True, "required": True},
        {"key": "category", "label": "类型", "type": "str", "editable": True, "required": False},
        {"key": "operator_id", "label": "操作者ID", "type": "int", "editable": True, "required": True},
        {"key": "created_at", "label": "创建时间", "type": "datetime", "editable": False, "required": False},
    ],
    "points_rules": [
        {"key": "id", "label": "ID", "type": "int", "editable": False, "required": False},
        {"key": "name", "label": "规则名称", "type": "str", "editable": True, "required": True},
        {"key": "points", "label": "积分", "type": "int", "editable": True, "required": True},
        {"key": "category", "label": "类型", "type": "str", "editable": True, "required": False},
        {"key": "icon", "label": "图标", "type": "str", "editable": True, "required": False},
        {"key": "is_active", "label": "启用", "type": "bool", "editable": True, "required": False},
        {"key": "owner_id", "label": "所属用户ID", "type": "int", "editable": True, "required": True},
        {"key": "created_at", "label": "创建时间", "type": "datetime", "editable": False, "required": False},
    ],
    "badges": [
        {"key": "id", "label": "ID", "type": "int", "editable": False, "required": False},
        {"key": "name", "label": "勋章名称", "type": "str", "editable": True, "required": True},
        {"key": "icon", "label": "图标", "type": "str", "editable": True, "required": False},
        {"key": "description", "label": "描述", "type": "str", "editable": True, "required": False},
        {"key": "owner_id", "label": "所属用户ID", "type": "int", "editable": True, "required": True},
        {"key": "created_at", "label": "创建时间", "type": "datetime", "editable": False, "required": False},
    ],
    "student_badges": [
        {"key": "id", "label": "ID", "type": "int", "editable": False, "required": False},
        {"key": "student_id", "label": "学生ID", "type": "int", "editable": True, "required": True},
        {"key": "badge_id", "label": "勋章ID", "type": "int", "editable": True, "required": True},
        {"key": "awarded_at", "label": "颁发时间", "type": "datetime", "editable": False, "required": False},
        {"key": "awarded_by", "label": "颁发者ID", "type": "int", "editable": True, "required": True},
    ],
    "login_logs": [
        {"key": "id", "label": "ID", "type": "int", "editable": False, "required": False},
        {"key": "username", "label": "用户名", "type": "str", "editable": True, "required": True},
        {"key": "ip_address", "label": "IP地址", "type": "str", "editable": True, "required": False},
        {"key": "success", "label": "成功", "type": "bool", "editable": True, "required": False},
        {"key": "fail_reason", "label": "失败原因", "type": "str", "editable": True, "required": False},
        {"key": "created_at", "label": "创建时间", "type": "datetime", "editable": False, "required": False},
    ],
}

# 隐藏的敏感字段
HIDDEN_FIELDS = {"password_hash"}


def _serialize_row(row, columns):
    """将ORM对象序列化为dict"""
    data = {}
    for col in columns:
        key = col["key"]
        if key in HIDDEN_FIELDS:
            data[key] = "***"
            continue
        val = getattr(row, key, None)
        if isinstance(val, datetime):
            data[key] = val.isoformat()
        else:
            data[key] = val
    return data


router = APIRouter(prefix="/api/admin", tags=["管理后台"])


def _require_admin(user: User = Depends(get_current_user)) -> User:
    """校验管理员权限"""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


@router.get("/stats")
async def system_stats(
    user: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """系统统计概览"""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())

    user_count = (await db.execute(select(func.count(User.id)))).scalar() or 0
    class_count = (await db.execute(select(func.count(Class.id)))).scalar() or 0
    student_count = (await db.execute(select(func.count(Student.id)))).scalar() or 0
    badge_count = (await db.execute(select(func.count(Badge.id)))).scalar() or 0
    total_points = (await db.execute(select(func.coalesce(func.sum(Student.points), 0)))).scalar()
    total_records = (await db.execute(select(func.count(PointsLog.id)))).scalar() or 0

    today_records = (await db.execute(
        select(func.count(PointsLog.id)).where(PointsLog.created_at >= today_start)
    )).scalar() or 0

    week_records = (await db.execute(
        select(func.count(PointsLog.id)).where(PointsLog.created_at >= week_start)
    )).scalar() or 0

    # 最近7天每日积分记录数
    daily_stats = []
    for i in range(6, -1, -1):
        day = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        next_day = day + timedelta(days=1)
        count = (await db.execute(
            select(func.count(PointsLog.id)).where(
                PointsLog.created_at >= day, PointsLog.created_at < next_day
            )
        )).scalar() or 0
        daily_stats.append({"date": day.strftime("%m-%d"), "count": count})

    # 最近登录日志
    login_logs_result = await db.execute(
        select(LoginLog).order_by(LoginLog.created_at.desc()).limit(10)
    )
    recent_logins = [
        {
            "username": log.username,
            "ip_address": log.ip_address,
            "success": log.success,
            "fail_reason": log.fail_reason,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in login_logs_result.scalars().all()
    ]

    return {
        "overview": {
            "user_count": user_count,
            "class_count": class_count,
            "student_count": student_count,
            "badge_count": badge_count,
            "total_points": total_points,
            "total_records": total_records,
            "today_records": today_records,
            "week_records": week_records,
        },
        "daily_stats": daily_stats,
        "recent_logins": recent_logins,
        "system": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "app_version": settings.APP_VERSION,
        },
    }


@router.get("/users")
async def list_users(
    user: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """用户列表"""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "display_name": u.display_name,
            "is_admin": u.is_admin,
            "expires_at": u.expires_at.isoformat() if u.expires_at else None,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


@router.post("/users")
async def create_user(
    data: dict,
    user: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """创建用户"""
    username = data.get("username", "").strip()
    password = data.get("password", "")
    display_name = data.get("display_name", username)

    if not username or not password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="密码长度至少8位")

    exists = await db.execute(select(User).where(User.username == username))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    new_user = User(
        username=username,
        password_hash=hash_password(password),
        display_name=display_name,
    )
    db.add(new_user)
    await db.flush()
    return {"message": "创建成功", "id": new_user.id}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    user: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """删除用户（级联清理关联数据）"""
    if user_id == user.id:
        raise HTTPException(status_code=400, detail="不能删除自己")

    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 级联清理：先删学生关联数据，再删学生，再删班级

    # 获取该用户所有班级
    classes_result = await db.execute(select(Class.id).where(Class.owner_id == user_id))
    class_ids = [row[0] for row in classes_result.all()]

    if class_ids:
        # 获取所有学生 ID
        students_result = await db.execute(select(Student.id).where(Student.class_id.in_(class_ids)))
        student_ids = [row[0] for row in students_result.all()]

        if student_ids:
            # 删除学生的积分日志和勋章关联
            await db.execute(
                PointsLog.__table__.delete().where(PointsLog.student_id.in_(student_ids))
            )
            await db.execute(
                StudentBadge.__table__.delete().where(StudentBadge.student_id.in_(student_ids))
            )
        # 删除学生
        await db.execute(Student.__table__.delete().where(Student.class_id.in_(class_ids)))
        # 删除班级
        await db.execute(Class.__table__.delete().where(Class.owner_id == user_id))

    # 删除该用户的勋章、积分规则、颁发的勋章记录
    await db.execute(Badge.__table__.delete().where(Badge.owner_id == user_id))
    await db.execute(PointsRule.__table__.delete().where(PointsRule.owner_id == user_id))
    await db.execute(StudentBadge.__table__.delete().where(StudentBadge.awarded_by == user_id))

    await db.delete(target)
    return {"message": "已删除"}


@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    data: dict,
    user: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """重置用户密码"""
    new_password = data.get("new_password", "")
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="密码长度至少8位")

    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")

    target.password_hash = hash_password(new_password)
    await db.flush()
    return {"message": "密码已重置"}


@router.put("/users/{user_id}/expiry")
async def update_user_expiry(
    user_id: int,
    data: dict,
    user: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """设置用户账号有效期"""
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")

    expires_at_str = data.get("expires_at")
    if expires_at_str:
        try:
            target.expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式无效")
    else:
        target.expires_at = None

    await db.flush()
    return {"message": "有效期已更新"}


@router.get("/login-logs")
async def get_login_logs(
    limit: int = Query(100, ge=1, le=500),
    success_only: bool = Query(False),
    user: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """登录日志查询"""
    query = select(LoginLog).order_by(LoginLog.created_at.desc())
    if success_only:
        query = query.where(LoginLog.success == True)
    query = query.limit(limit)

    result = await db.execute(query)
    logs = result.scalars().all()
    return [
        {
            "id": log.id,
            "username": log.username,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent[:100] if log.user_agent else "",
            "success": log.success,
            "fail_reason": log.fail_reason,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]


@router.get("/points-logs")
async def get_points_logs(
    limit: int = Query(100, ge=1, le=500),
    user: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """积分操作日志"""
    result = await db.execute(
        select(PointsLog).order_by(PointsLog.created_at.desc()).limit(limit)
    )
    logs = result.scalars().all()
    return [
        {
            "id": log.id,
            "student_id": log.student_id,
            "points": log.points,
            "reason": log.reason,
            "category": log.category,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]


@router.post("/backup")
async def manual_backup(
    user: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """手动备份（导出关键数据为JSON）"""
    import json

    data = {}
    users = (await db.execute(select(User))).scalars().all()
    data["users"] = [{"id": u.id, "username": u.username, "display_name": u.display_name, "is_admin": u.is_admin, "created_at": u.created_at.isoformat() if u.created_at else None} for u in users]

    classes = (await db.execute(select(Class))).scalars().all()
    data["classes"] = [{"id": c.id, "name": c.name, "description": c.description, "owner_id": c.owner_id} for c in classes]

    students = (await db.execute(select(Student))).scalars().all()
    data["students"] = [
        {"id": s.id, "student_no": s.student_no, "name": s.name, "points": s.points, "class_id": s.class_id}
        for s in students
    ]

    logs = (await db.execute(select(PointsLog))).scalars().all()
    data["points_logs"] = [{"id": l.id, "student_id": l.student_id, "points": l.points, "reason": l.reason, "category": l.category, "created_at": l.created_at.isoformat() if l.created_at else None} for l in logs]

    badges = (await db.execute(select(Badge))).scalars().all()
    data["badges"] = [{"id": b.id, "name": b.name, "icon": b.icon, "description": b.description} for b in badges]

    now = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    content = json.dumps(data, ensure_ascii=False, indent=2)

    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=sps_backup_{now}.json"},
    )


# 数据库可视化 CRUD API

TABLE_LABELS = {
    "users": "用户",
    "classes": "班级",
    "students": "学生",
    "points_logs": "积分记录",
    "points_rules": "积分规则",
    "badges": "勋章",
    "student_badges": "学生勋章",
    "login_logs": "登录日志",
}


@router.get("/db/tables")
async def list_tables(user: User = Depends(_require_admin)):
    """返回所有可管理的表及其列定义"""
    tables = []
    for name, cols in TABLE_COLUMNS.items():
        tables.append({
            "name": name,
            "label": TABLE_LABELS.get(name, name),
            "columns": [c for c in cols if c["key"] not in HIDDEN_FIELDS],
        })
    return tables


@router.get("/db/{table_name}")
async def db_list_rows(
    table_name: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    search: str = Query("", description="搜索关键词"),
    user: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """分页查询表数据"""
    if table_name not in TABLE_MODELS:
        raise HTTPException(400, f"不支持的表: {table_name}")

    model = TABLE_MODELS[table_name]
    columns = TABLE_COLUMNS[table_name]

    query = select(model)
    count_query = select(func.count()).select_from(model)

    # 搜索：对所有str类型字段做LIKE
    if search:
        from ..utils.sanitize import escape_like
        safe_search = escape_like(search)
        conditions = []
        for col in columns:
            if col["type"] == "str" and col["key"] not in HIDDEN_FIELDS:
                attr = getattr(model, col["key"], None)
                if attr is not None:
                    conditions.append(attr.ilike(f"%{safe_search}%", escape="\\"))
        if conditions:
            query = query.where(or_(*conditions))
            count_query = count_query.where(or_(*conditions))

    total = (await db.execute(count_query)).scalar() or 0
    query = query.order_by(model.id.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    rows = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "rows": [_serialize_row(r, columns) for r in rows],
    }


@router.post("/db/{table_name}")
async def db_create_row(
    table_name: str,
    data: dict,
    user: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """新增一行"""
    if table_name not in TABLE_MODELS:
        raise HTTPException(400, f"不支持的表: {table_name}")

    model = TABLE_MODELS[table_name]
    columns = {c["key"]: c for c in TABLE_COLUMNS[table_name]}

    kwargs = {}
    for key, col in columns.items():
        if key in ("id",) or not col.get("editable", True):
            continue
        if key in data and data[key] is not None and data[key] != "":
            val = data[key]
            if col["type"] == "int":
                val = int(val)
            elif col["type"] == "float":
                val = float(val)
            elif col["type"] == "bool":
                val = bool(val) if not isinstance(val, str) else val.lower() in ("true", "1", "yes")
            kwargs[key] = val
        elif col.get("required"):
            raise HTTPException(400, f"缺少必填字段: {col['label']}")

    obj = model(**kwargs)
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return _serialize_row(obj, TABLE_COLUMNS[table_name])


@router.put("/db/{table_name}/{row_id}")
async def db_update_row(
    table_name: str,
    row_id: int,
    data: dict,
    user: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """更新一行"""
    if table_name not in TABLE_MODELS:
        raise HTTPException(400, f"不支持的表: {table_name}")

    model = TABLE_MODELS[table_name]
    columns = {c["key"]: c for c in TABLE_COLUMNS[table_name]}

    result = await db.execute(select(model).where(model.id == row_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "记录不存在")

    for key, col in columns.items():
        if not col.get("editable", True):
            continue
        if key in data:
            val = data[key]
            if val == "" and not col.get("required"):
                val = None
            if val is not None:
                if col["type"] == "int":
                    val = int(val)
                elif col["type"] == "float":
                    val = float(val)
                elif col["type"] == "bool":
                    val = bool(val) if not isinstance(val, str) else val.lower() in ("true", "1", "yes")
            setattr(obj, key, val)

    await db.flush()
    await db.refresh(obj)
    return _serialize_row(obj, TABLE_COLUMNS[table_name])


@router.delete("/db/{table_name}/{row_id}")
async def db_delete_row(
    table_name: str,
    row_id: int,
    user: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """删除一行"""
    if table_name not in TABLE_MODELS:
        raise HTTPException(400, f"不支持的表: {table_name}")

    model = TABLE_MODELS[table_name]
    result = await db.execute(select(model).where(model.id == row_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "记录不存在")

    await db.delete(obj)
    await db.flush()
    return {"message": "已删除", "id": row_id}
