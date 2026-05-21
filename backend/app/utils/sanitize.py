"""输入清洗工具：XSS 防护 + 通配符转义"""
import re


# 危险标签和属性（不区分大小写匹配）
_DANGEROUS_PATTERNS = [
    r"<\s*script", r"<\s*/\s*script",
    r"<\s*iframe", r"<\s*object", r"<\s*embed", r"<\s*form",
    r"<\s*img\b[^>]*\bon\w+\s*=",  # onerror, onload 等
    r"<\s*svg\b[^>]*\bon\w+\s*=",
    r"<\s*\w+\b[^>]*\bon\w+\s*=",  # 任意标签的 on* 事件
    r"javascript\s*:", r"vbscript\s*:", r"data\s*:",
    r"expression\s*\(", r"url\s*\(",
]
_DANGEROUS_RE = re.compile("|".join(_DANGEROUS_PATTERNS), re.IGNORECASE)


def sanitize_text(v: str) -> str:
    """基础 XSS 过滤：检测危险模式并拒绝"""
    if _DANGEROUS_RE.search(v):
        raise ValueError("包含不允许的字符或标签")
    return v.strip()


def escape_like(v: str) -> str:
    """转义 SQL LIKE 通配符"""
    return v.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
