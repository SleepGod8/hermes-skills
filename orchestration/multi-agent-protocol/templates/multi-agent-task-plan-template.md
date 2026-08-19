# 多 Agent 开发任务计划

> 项目：{{PROJECT_NAME}}
> 本轮 ID：{{ROUND_ID}}
> 负责人：Athena / default
> 创建时间：{{CREATED_AT}}
> 工程宪法：{{CONSTITUTION_PATH}}

## 0. 使用规则

1. 所有 Agent 开工前必须先读取并遵守 `{{CONSTITUTION_PATH}}`。
2. 本计划只描述本轮执行安排；若与工程宪法或冻结契约冲突，以更高优先级文档为准。
3. 任何开发位不得修改未分配文件；需要越界时提交阻塞事项给 Athena 裁决。
4. 未冻结公共接口、schema、权限、配置、测试基建前，不得并行开发依赖它们的任务。

## 1. 本轮目标和非目标

### 目标

- {{GOAL_1}}
- {{GOAL_2}}

### 非目标

- {{NON_GOAL_1}}
- {{NON_GOAL_2}}

### 验收口径

- {{ACCEPTANCE_CRITERION_1}}
- {{ACCEPTANCE_CRITERION_2}}

## 2. 权威文档与优先级

| 优先级 | 文档/来源 | 用途 |
|---:|---|---|
| 1 | {{CONSTITUTION_PATH}} | 项目长期工程宪法 |
| 2 | {{CONTRACTS_OR_ADR}} | 冻结契约 / 架构决策 |
| 3 | {{TASK_BOOK_PATH}} | 本轮任务书 |
| 4 | `.agents/*` | 本轮状态、文件锁、报告 |
| 5 | 当前聊天 | 临时说明，不能覆盖高优先级文档 |

## 3. 任务依赖图

```mermaid
flowchart TD
  T0[{{SERIAL_TASK_0}}] --> T1[{{PARALLEL_TASK_1}}]
  T0 --> T2[{{PARALLEL_TASK_2}}]
  T1 --> V[Eos 验收]
  T2 --> V
```

## 4. 串行前置任务

| ID | 任务 | 负责人 | 文件范围 | Done 条件 | 验证命令 | 风险 |
|---|---|---|---|---|---|---|
| S1 | {{SERIAL_TASK_1}} | Hypnos/Athena | {{FILES}} | {{DONE}} | `{{VERIFY_CMD}}` | {{RISK}} |

## 5. 可并行任务池

只有通过“并行判定表”的任务才能进入本表。

| ID | 任务 | 负责人 | 文件范围 | 依赖 | Done 条件 | 验证命令 |
|---|---|---|---|---|---|---|
| P1 | {{TASK}} | Hebe | {{FILES}} | {{DEPENDS}} | {{DONE}} | `{{VERIFY_CMD}}` |
| P2 | {{TASK}} | Artemis | {{FILES}} | {{DEPENDS}} | {{DONE}} | `{{VERIFY_CMD}}` |
| P3 | {{TASK}} | Nemesis | {{FILES}} | {{DEPENDS}} | {{DONE}} | `{{VERIFY_CMD}}` |

## 6. 文件所有权矩阵

| 路径/文件 | Owner | 可读 Agent | 可写 Agent | 锁状态 | 备注 |
|---|---|---|---|---|---|
| {{PATH}} | {{OWNER}} | all | {{WRITER}} | unlocked | {{NOTE}} |

## 7. Agent 分配表

| Agent | 角色 | 模型层 | 任务 ID | 输入上下文 | 输出产物 |
|---|---|---|---|---|---|
| Athena | 项目负责人 | 稳态层 | S/A | 工程宪法、任务计划 | 裁决、派工、集成 |
| Hypnos | 架构侦察 | 重推理层 | S1 | 代码/契约 | 架构报告/接口冻结 |
| Hebe | 开发位 1 | 主力层 | P1 | 任务书+文件范围 | 代码+测试+验证证据 |
| Artemis | 开发位 2 | 主力层 | P2 | 任务书+文件范围 | 代码+测试+验证证据 |
| Nemesis | 开发位 3 | 主力层 | P3 | 任务书+文件范围 | 代码+测试+验证证据 |
| Eos | 测试/审查 | 稳态层 | V | diff+测试输出 | PASS/REJECT 报告 |

## 8. 验收矩阵

| 验收项 | 验收者 | 命令/证据 | 通过标准 |
|---|---|---|---|
| 工程宪法遵从 | Eos | 代码审查 | 无禁止项/越权修改 |
| 单元测试 | 开发位/Eos | `{{UNIT_TEST_CMD}}` | 通过 |
| 类型/静态检查 | 开发位/Eos | `{{LINT_TYPE_CMD}}` | 通过 |
| 集成回归 | Athena/Eos | `{{INTEGRATION_CMD}}` | 通过或说明未执行原因 |

## 9. 风险与回滚

| 风险 | 等级 | 影响 | 缓解措施 | 回滚方式 |
|---|---|---|---|---|
| {{RISK}} | {{LOW_MED_HIGH}} | {{IMPACT}} | {{MITIGATION}} | {{ROLLBACK}} |

## 10. 主人待确认事项

| 编号 | 问题 | 建议默认 | 不采纳后果 | 是否阻塞 |
|---|---|---|---|---|
| Q1 | {{QUESTION}} | {{DEFAULT}} | {{CONSEQUENCE}} | YES/NO |

## 11. 最终汇报格式

```text
结果：完成/部分完成/阻塞
主要修改：...
验证：命令 + 真实输出摘要
审查：Eos PASS/REJECT + 缺陷清单
风险：剩余风险与未验证项
下一步：...
```
