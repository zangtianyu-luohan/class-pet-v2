# Change: 修复抽奖功能 API 调用

## Why
Tools.vue 中积分抽奖功能调用了不存在的 API 路径 `/api/students/${id}/points`，导致抽奖后积分变动无法生效。正确的接口是 `POST /api/students/points/adjust`，请求体需要 `student_id` 字段。

## What Changes
- 修复 Tools.vue 中两处抽奖 API 调用（第 604 行和第 610 行）
- 将 `/api/students/${student.id}/points` 改为 `/api/students/points/adjust`
- 将请求体中的积分字段与 `student_id` 一起传入

## Out of Scope
- 不修改后端接口（后端已正确实现）
- 不修改抽奖逻辑本身（奖项配置、权重、动画）
- 不修改其他工具的 API 调用

## Impact
- 受影响文件：`frontend/src/views/Tools.vue`
- 受影响功能：积分抽奖（仅此一个功能）
- 无数据库变更，无 API 变更
