# 多 Agent 开工产物清单

按任务复杂度选择流程重量。不要小题大做，也不要高风险任务省略门禁。

## 1. 轻量模式

适用：单文件/小范围修改、低风险、无公共接口/数据库/权限/配置变更。

必须产物：

- `PROJECT_CONSTITUTION.md` 或既有 `AGENTS.md`：可复用项目规范；若已存在且未过期，只需读取。
- 简短任务计划：可在聊天中列出，或写 `TASK_PLAN.md`。
- 文件级验证命令清单。
- 最终验证证据。

推荐队形：`default` 直接做，必要时 `Eos` 验证。

## 2. 标准模式

适用：单模块功能、多人/多 Agent 协作、有明确文件边界、需要任务书。

必须产物：

- `PROJECT_CONSTITUTION.md` / `AGENTS.md`
- `.agents/project-brief.md`
- `.agents/task-board.yaml`
- `.agents/module-ownership.yaml`
- Agent 任务书：如 `RISK-*-TASK.md` / `DOMAIN-*-TASK.md`
- 验收矩阵或 Eos 审查报告

推荐队形：`Athena + Hypnos + 1-3 个开发位 + Eos`。

## 3. 重型模式

适用：跨模块重构、公共接口/数据库/权限/配置/部署/外部服务、生产风险高。

必须产物：

- 标准模式全部产物
- `.agents/architecture.md`
- `.agents/contracts/`
- `.agents/decisions/` ADR
- `.agents/checkpoints/`，包含模型切换/恢复记录
- `.agents/test-reports/`
- `.agents/release-checklist.md`
- 回滚方案与发布观察责任人

推荐队形：主队全开；候补位按产能/表达/探索缺口启用。

## 4. 升级规则

出现以下任一情况，至少升级到标准模式：

- 需要两个以上 Agent 并行。
- 涉及多个模块或多文件所有权。
- 需要生成给开发位执行的任务书。

出现以下任一情况，升级到重型模式：

- 数据库 schema / migration。
- 权限、认证、安全、配置、CI/CD、部署。
- 公共接口或跨模块数据结构。
- 外部 API、支付、消息发送、生产数据或不可逆副作用。
