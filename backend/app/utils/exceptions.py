"""
全局异常处理器
- 隐藏数据库错误细节
- 统一错误返回格式
- 防止 SQL 注入信息泄露
"""
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError

logger = logging.getLogger(__name__)


async def integrity_error_handler(request: Request, exc: IntegrityError):
    """数据库完整性错误（唯一约束、外键等）"""
    logger.warning(f"IntegrityError: {exc.orig}")
    return JSONResponse(
        status_code=400,
        content={"detail": "数据冲突，请检查输入内容是否重复"},
    )


async def operational_error_handler(request: Request, exc: OperationalError):
    """数据库连接/操作错误"""
    logger.error(f"OperationalError: {exc.orig}")
    return JSONResponse(
        status_code=503,
        content={"detail": "数据库暂时不可用，请稍后重试"},
    )


async def programming_error_handler(request: Request, exc: ProgrammingError):
    """SQL 语法错误"""
    logger.error(f"ProgrammingError: {exc.orig}")
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误"},
    )


async def generic_error_handler(request: Request, exc: Exception):
    """兜底：所有未处理的异常"""
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误，请稍后重试"},
    )
