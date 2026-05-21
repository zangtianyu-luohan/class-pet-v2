"""
登录安全模块
- 登录失败锁定（5次失败锁15分钟）
- 登录日志记录
- 图形验证码
"""
import io
import random
import string
import time
import hashlib
from collections import defaultdict
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from ..database import Base


# ========== 登录失败锁定 ==========
class LoginAttemptTracker:
    """内存级登录失败追踪（重启清空，够用）"""

    def __init__(self, max_attempts: int = 5, lockout_seconds: int = 900):
        self.max_attempts = max_attempts
        self.lockout_seconds = lockout_seconds
        self._attempts: dict[str, list[float]] = defaultdict(list)

    def record_failure(self, key: str):
        """记录一次失败"""
        now = time.time()
        self._attempts[key].append(now)
        # 只保留窗口内的记录
        cutoff = now - self.lockout_seconds
        self._attempts[key] = [t for t in self._attempts[key] if t > cutoff]

    def is_locked(self, key: str) -> tuple[bool, int]:
        """检查是否被锁定，返回 (是否锁定, 剩余秒数)"""
        now = time.time()
        cutoff = now - self.lockout_seconds
        recent = [t for t in self._attempts[key] if t > cutoff]
        self._attempts[key] = recent

        if len(recent) >= self.max_attempts:
            remaining = int(self.lockout_seconds - (now - recent[0]))
            return True, max(remaining, 0)
        return False, 0

    def clear(self, key: str):
        """登录成功后清除"""
        self._attempts.pop(key, None)


login_tracker = LoginAttemptTracker()


# ========== 登录日志 ==========
class LoginLog(Base):
    __tablename__ = "login_logs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, index=True)
    ip_address = Column(String(50), default="")
    user_agent = Column(String(500), default="")
    success = Column(Boolean, default=False)
    fail_reason = Column(String(200), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ========== 图形验证码 ==========
class CaptchaStore:
    """内存级验证码存储"""

    def __init__(self, expire_seconds: int = 120):
        self.expire_seconds = expire_seconds
        self._store: dict[str, tuple[str, float]] = {}

    def generate(self, key: str) -> str:
        """生成验证码，返回答案"""
        # 简单数学题：两位数加减法
        a = random.randint(10, 50)
        b = random.randint(1, 20)
        op = random.choice(["+", "-"])
        if op == "-" and a < b:
            a, b = b, a
        answer = str(a + b) if op == "+" else str(a - b)
        question = f"{a} {op} {b} = ?"
        self._store[key] = (answer, time.time() + self.expire_seconds)
        return question

    def verify(self, key: str, answer: str) -> bool:
        """验证答案"""
        entry = self._store.pop(key, None)
        if not entry:
            return False
        expected, expire_at = entry
        if time.time() > expire_at:
            return False
        return answer.strip() == expected


captcha_store = CaptchaStore()


def generate_captcha_image(question: str) -> bytes:
    """生成验证码图片（纯 Python，无需 Pillow）"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGB", (160, 60), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        # 干扰线
        for _ in range(5):
            x1, y1 = random.randint(0, 160), random.randint(0, 60)
            x2, y2 = random.randint(0, 160), random.randint(0, 60)
            color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
            draw.line([(x1, y1), (x2, y2)], fill=color, width=1)

        # 文字（跨平台字体路径）
        font = None
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",      # Windows 微软雅黑
            "C:/Windows/Fonts/simhei.ttf",     # Windows 黑体
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "/System/Library/Fonts/PingFang.ttc",  # macOS
        ]
        for fp in font_paths:
            try:
                font = ImageFont.truetype(fp, 24)
                break
            except (OSError, IOError):
                continue
        if font is None:
            font = ImageFont.load_default()

        draw.text((20, 15), question, fill=(50, 50, 150), font=font)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except ImportError:
        # 无 Pillow 时返回纯文本 SVG
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="60">
        <rect width="160" height="60" fill="#f0f0f0"/>
        <text x="20" y="40" font-size="24" fill="#333" font-family="monospace">{question}</text>
        </svg>'''
        return svg.encode()
