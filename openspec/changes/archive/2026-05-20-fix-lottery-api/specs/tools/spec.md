## MODIFIED Requirements
### Requirement: 积分抽奖
课堂工具页面 SHALL 提供积分抽奖功能，抽奖结果 SHALL 通过 `POST /api/students/points/adjust` 接口正确更新学生积分。

#### Scenario: 抽奖中奖加分
- **WHEN** 学生抽中"积分 ×3"奖项
- **THEN** 系统调用 `/api/students/points/adjust`，传入 `student_id`、`points` 为 `lotteryCost * 2`、`reason` 为"抽奖{奖项名}"、`category` 为"lottery"

#### Scenario: 抽奖参与奖减分
- **WHEN** 学生抽中"积分不变"奖项（delta === 0）
- **THEN** 系统调用 `/api/students/points/adjust`，传入 `student_id`、`points` 为 `-lotteryCost`、`reason` 为"抽奖参与奖"、`category` 为"lottery"
