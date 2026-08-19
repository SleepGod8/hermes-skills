# 多 Agent 并行开发判定表

> 用途：Athena 派工前判断任务能否并行。只有全部关键项为 YES，才允许并行。

## 1. 判定结论

| 项 | 内容 |
|---|---|
| 本轮任务 | {{ROUND_ID}} |
| 判定人 | Athena / default |
| 结论 | 可并行 / 不可并行 / 需先串行冻结框架 |
| 原因摘要 | {{SUMMARY}} |

## 2. 必须全部 YES 的条件

| 编号 | 检查项 | YES/NO | 证据/说明 |
|---|---|---|---|
| P1 | 任务之间不修改同一文件 | {{YES_NO}} | {{EVIDENCE}} |
| P2 | 不修改同一公共接口/公共类型/基类 | {{YES_NO}} | {{EVIDENCE}} |
| P3 | 不修改同一数据库表 schema/迁移 | {{YES_NO}} | {{EVIDENCE}} |
| P4 | 不修改同一权限/认证/配置/CI 入口 | {{YES_NO}} | {{EVIDENCE}} |
| P5 | 上游接口、schema、测试基建已冻结 | {{YES_NO}} | {{EVIDENCE}} |
| P6 | 任务之间没有顺序依赖 | {{YES_NO}} | {{EVIDENCE}} |
| P7 | 每个任务有独立验收标准 | {{YES_NO}} | {{EVIDENCE}} |
| P8 | 每个任务有可独立运行的验证命令 | {{YES_NO}} | {{EVIDENCE}} |
| P9 | 任一任务失败不会污染其他任务 | {{YES_NO}} | {{EVIDENCE}} |
| P10 | 文件所有权已记录到任务计划或 `.agents/module-ownership.yaml` | {{YES_NO}} | {{EVIDENCE}} |

## 3. 若不可并行，串行前置任务

| ID | 前置任务 | 负责人 | Done 条件 |
|---|---|---|---|
| S1 | {{SERIAL_TASK}} | Hypnos/Athena | {{DONE}} |

## 4. 可并行任务清单

| ID | 任务 | 负责人 | 文件范围 | 验证命令 |
|---|---|---|---|---|
| P1 | {{TASK}} | Hebe | {{FILES}} | `{{CMD}}` |
