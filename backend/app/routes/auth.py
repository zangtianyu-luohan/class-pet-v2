import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models.user import User
from ..schemas.user import UserRegister, UserLogin, UserOut, Token, UserUpdate, PasswordChange
from ..utils.auth import hash_password, verify_password, create_access_token
from ..utils.deps import get_current_user
from ..utils.login_security import login_tracker, LoginLog, captcha_store, generate_captcha_image

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["认证"])


def _get_client_ip(request: Request) -> str:
    return request.headers.get("X-Forwarded-For", request.client.host if request.client else "").split(",")[0].strip()


@router.post("/register", response_model=Token)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        display_name=data.display_name,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
async def login(data: UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
    ip = _get_client_ip(request)
    lock_key = f"{data.username}:{ip}"

    # 检查是否被锁定
    locked, remaining = login_tracker.is_locked(lock_key)
    if locked:
        # 记录锁定日志
        db.add(LoginLog(username=data.username, ip_address=ip,
                        user_agent=str(request.headers.get("User-Agent", ""))[:500],
                        success=False, fail_reason=f"账号锁定，剩余{remaining}秒"))
        await db.flush()
        raise HTTPException(status_code=423, detail=f"登录失败次数过多，请 {remaining} 秒后重试")

    # 验证码校验
    if data.captcha_id and data.captcha_answer:
        if not captcha_store.verify(data.captcha_id, data.captcha_answer):
            db.add(LoginLog(username=data.username, ip_address=ip,
                            user_agent=str(request.headers.get("User-Agent", ""))[:500],
                            success=False, fail_reason="验证码错误"))
            await db.flush()
            raise HTTPException(status_code=400, detail="验证码错误")
    elif data.captcha_id is None:
        # 如果没传验证码，生成一个要求前端获取
        raise HTTPException(status_code=400, detail="请先获取验证码")

    # 查找用户
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        # 记录失败
        login_tracker.record_failure(lock_key)
        fail_reason = "用户不存在" if not user else "密码错误"
        db.add(LoginLog(username=data.username, ip_address=ip,
                        user_agent=str(request.headers.get("User-Agent", ""))[:500],
                        success=False, fail_reason=fail_reason))
        await db.flush()

        # 检查是否刚好触发锁定
        locked, remaining = login_tracker.is_locked(lock_key)
        if locked:
            raise HTTPException(status_code=423, detail=f"登录失败次数过多，账号已锁定 {remaining} 秒")
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 检查账号是否过期
    if user.expires_at:
        from datetime import datetime, timezone
        if datetime.now(timezone.utc) > user.expires_at:
            db.add(LoginLog(username=data.username, ip_address=ip,
                            user_agent=str(request.headers.get("User-Agent", ""))[:500],
                            success=False, fail_reason="账号已过期"))
            await db.flush()
            raise HTTPException(status_code=403, detail="账号已过期，请联系管理员续期")

    # 登录成功
    login_tracker.clear(lock_key)
    db.add(LoginLog(username=data.username, ip_address=ip,
                    user_agent=str(request.headers.get("User-Agent", ""))[:500],
                    success=True))
    await db.flush()

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.get("/captcha")
async def get_captcha():
    """获取图形验证码"""
    import uuid
    captcha_id = str(uuid.uuid4())
    question = captcha_store.generate(captcha_id)
    image = generate_captcha_image(question)
    return Response(
        content=image,
        media_type="image/png",
        headers={"X-Captcha-Id": captcha_id}
    )


@router.get("/captcha/json")
async def get_captcha_json():
    """获取验证码（JSON 格式，前端可用文字展示）"""
    import uuid
    captcha_id = str(uuid.uuid4())
    question = captcha_store.generate(captcha_id)
    return {"captcha_id": captcha_id, "question": question}


@router.get("/me", response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)


@router.put("/me", response_model=UserOut)
async def update_me(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if data.display_name is not None:
        user.display_name = data.display_name
    if data.avatar is not None:
        user.avatar = data.avatar
    await db.flush()
    await db.refresh(user)
    return UserOut.model_validate(user)


@router.put("/password")
async def change_password(
    data: PasswordChange,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(data.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")
    user.password_hash = hash_password(data.new_password)
    await db.flush()
    return {"message": "密码修改成功"}


@router.get("/login-logs")
async def get_login_logs(
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查询登录日志（管理员用）"""
    result = await db.execute(
        select(LoginLog).order_by(LoginLog.created_at.desc()).limit(limit)
    )
    logs = result.scalars().all()
    return [
        {
            "id": log.id,
            "username": log.username,
            "ip_address": log.ip_address,
            "success": log.success,
            "fail_reason": log.fail_reason,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]
