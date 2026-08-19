# 多 Agent 项目开工 Runbook

> 触发：主人说“按多 Agent 流程开工/让 Athena 规划/多人协作开发”。本 runbook 是执行顺序，不替代项目工程宪法或岗位协议。

## 0. 复杂度定级

| 等级 | 判定 | 最小产物 |
|---|---|---|
| 轻量 | 单模块、低风险、无共享契约 | 工程宪法引用、简版 brief、验证记录 |
| 标准 | 多文件/多角色，有明确并行边界 | 完整 `.agents/` 控制面、任务书、Eos 验收 |
| 重型 | 跨服务/schema/权限/部署/高风险 | 标准全部 + ADR/冻结契约/回滚方案/主人裁决点 |

## 1. 加载与侦察

1. 加载 `multi-agent-protocol`。
2. 加载 `project-constitution-authoring`，读取 README、AGENTS、需求、架构、schema、CI、测试配置。
3. 加载 `multi-agent-project-preflight`，输出 DRI、冻结契约、数据缺口与风险。
4. 需要编码时加载语言/框架/TDD/高可靠开发 skill。

**门禁 G1：** 输入源已列明；事实、推断、待确认分开；否则不得派工。

## 2. 建立或更新工程宪法

1. 创建/更新 `PROJECT_CONSTITUTION.md` 或 `AGENTS.md`。
2. 记录版本、状态、适用范围、权威来源、变更历史和兼容性影响。
3. 若本轮要求与宪法冲突，写入冲突表，由 Athena/主人裁决。

**门禁 G2：** Athena 确认本轮引用的宪法路径和版本；任务书必须引用同一版本。

## 3. 初始化 `.agents/` 控制面

从 `templates/agents/` 复制到项目根目录 `.agents/`：

```text
project-brief.md
task-board.yaml
module-ownership.yaml
decisions.md
validation-log.md
risk-register.md
handoff.md
```

替换所有 `<...>` 占位符，并在 `project-brief.md`、`task-board.yaml` 中写入工程宪法版本。

**门禁 G3：** 标准/重型任务的 7 个文件存在，YAML 可解析，任务 ID 和文件所有权唯一。

## 4. Athena 规划与冻结

1. 写本轮目标、非目标、验收标准。
2. Hypnos 完成代码侦察和架构提案。
3. Athena 冻结共享 API、schema、权限、配置、事件契约和测试基建。
4. 用 `parallel-readiness-checklist.md` 判断是否可并行。
5. 用 `agent-task-book-authoring` 为每个开发位生成任务书。

**门禁 G4：** 每个任务都有 owner、依赖、文件范围、验证命令、回滚点；共享文件不存在重复写锁。

## 5. 认领与实现

1. Agent 将任务状态改为 `CLAIMED`，登记时间和文件锁。
2. 读取工程宪法、任务书和相关源码后再修改。
3. 只修改所有权范围内文件；发现契约冲突立即 `BLOCKED`。
4. 优先运行文件级测试，真实结果写入 `validation-log.md`。
5. 模型熔断或切换写入 `model-switch-record-template.md`。

**门禁 G5：** 不接受仅口头“完成”；必须有变更文件、命令、退出码和证据位置。

## 6. 审查、集成与验收

1. Eos 按宪法 Done Definition、任务书 acceptance、风险登记和验证日志审查。
2. Athena 按依赖顺序集成；共享契约先于功能分支。
3. 执行项目规定的最终 lint/typecheck/test/build/e2e；无法执行必须记录原因和风险。
4. Eos 给出 `PASS / CONDITIONAL_PASS / FAIL`，引用具体 V-ID。

**门禁 G6：** 只有 `PASS` 或主人接受的 `CONDITIONAL_PASS` 才能标记 `ACCEPTED`。

## 7. 交接与收尾

1. 更新 `task-board.yaml` 状态和证据。
2. 释放/转移 `module-ownership.yaml` 文件锁。
3. 填写 `handoff.md`：完成项、未完成项、验证证据、下一步、风险。
4. 若契约或长期规则改变，先升级工程宪法版本并更新变更历史。
5. default 汇报：完成内容、修改文件、验证结果、未决风险、后续动作。

## 异常恢复

- Agent 中断：接任者先读 `.agents/` 和 `handoff.md`，不得依赖旧聊天。
- 接口未冻结：退回 G4，暂停下游并行任务。
- 验证失败：任务回到 `IN_PROGRESS`，记录失败命令，不得删除失败证据。
- 宪法冲突：任务置为 `BLOCKED`，由 Athena/主人裁决；裁决写入 `decisions.md`。
- 回滚：按任务书回滚方案执行，并在风险/验证日志记录真实结果。

## 开工完成判定

- [ ] 工程宪法路径和版本已冻结
- [ ] `.agents/` 控制面符合复杂度要求
- [ ] DRI、文件所有权、依赖和共享契约明确
- [ ] 每个任务有任务书、验收标准和验证命令
- [ ] Eos 验收口径已提前定义
- [ ] 主人需裁决事项已列出
