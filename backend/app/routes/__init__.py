from .auth import router as auth_router
from .classes import router as classes_router
from .students import router as students_router
from .badges import router as badges_router
from .leaderboard import router as leaderboard_router
from .rules import router as rules_router
from .admin import router as admin_router

__all__ = [
    "auth_router", "classes_router", "students_router",
    "badges_router", "leaderboard_router", "rules_router",
    "admin_router",
]
