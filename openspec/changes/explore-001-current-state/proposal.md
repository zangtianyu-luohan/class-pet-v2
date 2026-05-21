# Explore 001：项目现状梳理

## 项目概况
面向教师的班级积分管理系统 v2.0，学生通过课堂表现获得积分，系统提供排行榜、勋章、课堂工具等激励机制。

## 已有页面（9 个）
| 页面 | 路径 | 功能 |
|------|------|------|
| Dashboard | /dashboard | 班级总览（学生数、总积分、人均积分、今日记录）+ 快捷操作 |
| Students | /students | 学生管理（CRUD、批量导入 Excel/文本、批量积分、导出 Excel） |
| StudentDetail | /students/:id | 学生详情（信息、积分记录、勋章） |
| Leaderboard | /leaderboard | 排行榜（积分榜 + 本周榜，前三名领奖台） |
| Badges | /badges | 勋章管理（创建勋章、颁发勋章、颁发记录） |
| Tools | /tools | 课堂工具（11 个：随机点名、计时器、随机分组、抽奖、积分兑换、积分阈值提醒、骰子、噪音检测、秒表、红绿灯、随机数） |
| PointsLogs | /points-logs | 积分日志（分页、搜索、筛选、日期范围、导出 Excel） |
| Classes | /classes | 班级管理（CRUD） |
| Settings | /settings | 系统设置 |

## 数据模型（6 张表）
| 表 | 核心字段 | 说明 |
|---|---------|------|
| users | username, password_hash, display_name, is_admin, expires_at | 教师账号 |
| classes | name, description, owner_id, is_active | 班级（软删除） |
| students | student_no, name, points, class_id | 学生（已移除 pet_type/pet_name/level/experience/avatar） |
| points_logs | student_id, points, reason, category, operator_id | 积分变动记录 |
| badges / student_badges | name, icon, description / student_id, badge_id, awarded_by | 勋章及颁发 |
| points_rules | name, points, category, icon, is_active, owner_id | 积分规则模板 |

## API 接口（7 组）
| 模块 | 前缀 | 核心接口 |
|------|------|---------|
| 认证 | /api/auth | register, login, me |
| 班级 | /api/classes | CRUD, /stats |
| 学生 | /api/students | CRUD, /batch, /points/adjust, /points/batch, /import-excel(桩), /export-csv |
| 勋章 | /api/badges | CRUD, /award, /records |
| 排行榜 | /api/leaderboard | /stats, /points, /week |
| 规则 | /api/rules | CRUD |
| 管理后台 | /admin | sqladmin 可视化管理 |

## 状态管理（Pinia）
- auth.js：token + user 信息，localStorage 持久化
- class.js：classes 列表 + currentClassId，localStorage 持久化，自动选择第一个班级

## 已发现的问题
| 问题 | 位置 | 严重程度 |
|------|------|---------|
| N+1 查询 | leaderboard / badges / classes 路由 | 中（数据量大时性能差） |
| 统计逻辑重复 | classes.py 和 leaderboard.py 各有一份 | 低（维护成本） |
| 抽奖调用错误 API | Tools.vue 调用 /api/students/${id}/points | 中（功能不可用） |
| Excel 导入桩函数 | students.py /import-excel 是 pass | 中（功能缺失） |
| 前端 catch 块为空 | 多个 Vue 组件 | 低（用户看不到错误信息） |

## 当前阶段判断
项目功能基本完整，处于"能用但有粗糙边缘"的状态。适合从修复已知问题或补齐缺失功能开始第一个 change。
