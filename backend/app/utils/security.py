"""
安全中间件
- CSP 响应头
- XSS 防护头
- 安全相关 HTTP 头
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        path = request.url.path

        # 管理后台页面需要内联脚本 + eval（Vue template 编译需要）
        if path.startswith("/admin-panel") or path.startswith("/admin-assets"):
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'"
            )
        else:
            # 前端 SPA：只需 self + unsafe-inline（Vite 构建产物无内联脚本，但保留兼容）
            csp = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'"
            )

        response.headers["Content-Security-Policy"] = csp

        # XSS 防护
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 移除服务器信息
        if "server" in response.headers:
            del response.headers["server"]

        return response
