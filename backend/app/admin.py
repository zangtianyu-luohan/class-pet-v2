from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from .database import engine
from .models.user import User
from .models.class_ import Class
from .models.student import Student
from .models.badge import Badge, StudentBadge
from .models.points_log import PointsLog, PointsRule
from .utils.auth import verify_password
from sqlalchemy import select
from .database import async_session


# 管理员认证后端
class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        async with async_session() as session:
            result = await session.execute(select(User).where(User.username == username))
            user = result.scalar_one_or_none()

        if user and verify_password(password, user.password_hash):
            request.session.update({"admin_user_id": user.id})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return "admin_user_id" in request.session


# ===== 管理视图 =====
class UserAdmin(ModelView, model=User):
    name = "用户"
    name_plural = "用户管理"
    icon = "fa-solid fa-user"
    column_list = [User.id, User.username, User.display_name, User.created_at]
    column_searchable_list = [User.username, User.display_name]
    column_labels = {
        User.id: "ID",
        User.username: "用户名",
        User.display_name: "显示名称",
        User.avatar: "头像",
        User.created_at: "注册时间",
    }
    can_create = False
    can_edit = True
    can_delete = False


class ClassAdmin(ModelView, model=Class):
    name = "班级"
    name_plural = "班级管理"
    icon = "fa-solid fa-school"
    column_list = [Class.id, Class.name, Class.description, Class.owner_id, Class.is_active, Class.created_at]
    column_searchable_list = [Class.name]
    column_labels = {
        Class.id: "ID",
        Class.name: "班级名称",
        Class.description: "描述",
        Class.owner_id: "所属教师ID",
        Class.is_active: "是否启用",
        Class.created_at: "创建时间",
    }


class StudentAdmin(ModelView, model=Student):
    name = "学生"
    name_plural = "学生管理"
    icon = "fa-solid fa-users"
    column_list = [Student.id, Student.student_no, Student.name, Student.pet_type, Student.points, Student.level, Student.class_id]
    column_searchable_list = [Student.name, Student.student_no]
    column_sortable_list = [Student.points, Student.level, Student.name]
    column_labels = {
        Student.id: "ID",
        Student.student_no: "学号",
        Student.name: "姓名",
        Student.pet_type: "萌宠类型",
        Student.pet_name: "萌宠名称",
        Student.points: "积分",
        Student.level: "等级",
        Student.experience: "经验值",
        Student.class_id: "班级ID",
    }


class BadgeAdmin(ModelView, model=Badge):
    name = "勋章"
    name_plural = "勋章管理"
    icon = "fa-solid fa-medal"
    column_list = [Badge.id, Badge.name, Badge.icon, Badge.description, Badge.owner_id]
    column_searchable_list = [Badge.name]
    column_labels = {
        Badge.id: "ID",
        Badge.name: "勋章名称",
        Badge.icon: "图标",
        Badge.description: "描述",
        Badge.owner_id: "创建者ID",
    }


class StudentBadgeAdmin(ModelView, model=StudentBadge):
    name = "颁发记录"
    name_plural = "颁发记录"
    icon = "fa-solid fa-award"
    column_list = [StudentBadge.id, StudentBadge.student_id, StudentBadge.badge_id, StudentBadge.awarded_by, StudentBadge.awarded_at]
    column_labels = {
        StudentBadge.id: "ID",
        StudentBadge.student_id: "学生ID",
        StudentBadge.badge_id: "勋章ID",
        StudentBadge.awarded_by: "颁发者ID",
        StudentBadge.awarded_at: "颁发时间",
    }
    can_edit = False


class PointsLogAdmin(ModelView, model=PointsLog):
    name = "积分记录"
    name_plural = "积分记录"
    icon = "fa-solid fa-chart-line"
    column_list = [PointsLog.id, PointsLog.student_id, PointsLog.points, PointsLog.reason, PointsLog.category, PointsLog.created_at]
    column_searchable_list = [PointsLog.reason]
    column_sortable_list = [PointsLog.points, PointsLog.created_at]
    column_labels = {
        PointsLog.id: "ID",
        PointsLog.student_id: "学生ID",
        PointsLog.points: "积分变动",
        PointsLog.reason: "原因",
        PointsLog.category: "类型",
        PointsLog.operator_id: "操作者ID",
        PointsLog.created_at: "时间",
    }
    can_edit = False
    can_create = False


class PointsRuleAdmin(ModelView, model=PointsRule):
    name = "积分规则"
    name_plural = "积分规则"
    icon = "fa-solid fa-list-check"
    column_list = [PointsRule.id, PointsRule.name, PointsRule.points, PointsRule.category, PointsRule.icon, PointsRule.is_active]
    column_labels = {
        PointsRule.id: "ID",
        PointsRule.name: "规则名称",
        PointsRule.points: "积分",
        PointsRule.category: "类别",
        PointsRule.icon: "图标",
        PointsRule.is_active: "是否启用",
    }


def setup_admin(app):
    """初始化管理后台"""
    authentication_backend = AdminAuth(secret_key="admin-secret-key-change-me")

    admin = Admin(
        app=app,
        engine=engine,
        authentication_backend=authentication_backend,
        title="🐾 班级OK萌宠 管理后台",
        logo_url="/admin/statics/logo.png",
        base_url="/admin",
    )

    admin.add_view(UserAdmin)
    admin.add_view(ClassAdmin)
    admin.add_view(StudentAdmin)
    admin.add_view(BadgeAdmin)
    admin.add_view(StudentBadgeAdmin)
    admin.add_view(PointsLogAdmin)
    admin.add_view(PointsRuleAdmin)

    return admin
