---
name: multi-agent-protocol
description: Use when 多agent开发。严格遵从多Agent协作协议与固定编制岗位文件。
---

# 多 Agent 项目协作协议

用户指定的多 Agent 开发必须严格遵从以下文件（完整原文保存于本技能 `references/` 目录）：

1. `references/multi-agent-protocol.md` — 《多 Agent 项目协作协议》：固定编制、三档模型分层、任务编号/状态机、认领释放、标准消息格式、文件所有权、合并顺序、候补位启用纪律、模型熔断与质量门禁。
2. `references/soul-00-standby.md` — 《预备役岗位》文件：未接入开发团队的待接入占位岗位。
3. `references/soul-07a-execution-reserve.md` — 《Agent 7A：执行候补（Ares）》岗位文件。
4. `references/soul-07b-expression-reserve.md` — 《Agent 7B：表达候补（Aphrodite）》岗位文件。
5. `references/soul-07c-exploration-reserve.md` — 《Agent 7C：发散候补（Dionysus）》岗位文件。
6. `references/governance-rules.md` — 《团队治理规则》。
7. `references/enhanced-pipeline.md` — 《增强版多 Agent 开发流水线规范》。
8. `references/workflow-retro-2026-08.md` — 《2026-08 工作流复盘新增要点》（v1.6，含合并方向 merge-base 核实、同步后全员可读性确认）。
9. `references/review-findings-calibration.md` — 《审查 Findings 结构化与置信度校准规范》。
10. `references/workflow-retro-2026-08-smart-wealth.md` — 《2026-08 smart-wealth 项目复盘新增要点》（v1.7，含验收状态机、环境口径登记表、日志噪音分级、运维进程台账、汇报四要素）。
11. `references/multi-agent-startup-runbook.md` — 《多 Agent 项目开工 Runbook》：复杂度定级、G1-G6 门禁、`.agents/` 初始化、派工、实现、验收、交接与异常恢复的可执行顺序。

## 使用方式

当用户要求进行多 Agent 开发时：

1. 加载本技能，并读取 `references/` 下全部相关文件。
2. 按“多 Agent 开工技能加载顺序”加载相关技能，先立项目工程宪法，再做预检、任务书和派工。
3. 先按固定编制选队形：`default` 总控中枢，`Athena/Hypnos/Hebe/Artemis/Nemesis/Eos` 为主队，`Ares/Aphrodite/Dionysus` 为候补军团。
4. 按协议执行：任务编号、状态机、标准消息格式、文件所有权、合并顺序、质量门禁。
5. 关键决定落到 `.agents/` 工件，不以聊天消息为唯一事实来源。

## 多 Agent 开工技能加载顺序

主人要求多 Agent 开发、多人协作开发、让 Athena/default 规划 agent 工作时，按以下顺序加载技能；除非任务明显是简单单文件修复，否则不要跳过前置步骤：

1. `multi-agent-protocol`：读取固定编制、模型分层、状态机、文件所有权和质量门禁。
2. `project-constitution-authoring`：读取需求/规范/代码现状，创建或更新 `PROJECT_CONSTITUTION.md` / `AGENTS.md` / `DEVELOPMENT_GUIDE.md`。
3. `multi-agent-project-preflight`：做开工预检，识别 DRI、冻结契约、数据缺口、待确认事项。
4. `agent-task-book-authoring`：为具体域/模块/开发位生成 Agent 可执行任务书。
5. 对应编码与验证技能：按项目语言和技术栈加载 `high-reliability-coding-workflow`、`python-engineering-workflow`、`test-driven-development`、框架专用 skill 等。
6. 审查与验收：由 `Eos` 或独立 reviewer 按项目工程宪法的 Done Definition、验证命令和本协议质量门禁执行。

## 文档优先级

多 Agent 协作时，所有 agent 按以下优先级解释需求和约束：

1. `PROJECT_CONSTITUTION.md` / `AGENTS.md` / `DEVELOPMENT_GUIDE.md`：项目级长期工程宪法。
2. 架构契约、ADR、冻结接口、数据库 schema、权限模型、CI/测试配置。
3. Agent 任务书：某一域/模块/角色的一次性执行契约。
4. `.agents/task-board.yaml`、`.agents/module-ownership.yaml`、`.agents/project-brief.md`：本轮执行状态与文件锁。
5. 当前聊天中的临时说明。

若低优先级内容与高优先级内容冲突，开发位必须停止并列出冲突，由 `Athena`/主人裁决；不得用聊天临时指令静默覆盖工程宪法或冻结契约。

## 核心要点速查

### 固定编制
- `default`：总控中枢、会话协调、汇总输出；多 Agent 开工前加载 `project-constitution-authoring`，确保存在项目工程宪法
- `Athena`：Agent 1，项目负责人、集成与发布；负责确认/维护 `PROJECT_CONSTITUTION.md` / `AGENTS.md` 等项目工程宪法，并据此派工
- `Hypnos`：Agent 2，代码侦察与架构设计；设计前必须读取项目工程宪法
- `Hebe`：Agent 3，功能开发 1；实现前必须读取项目工程宪法和任务书
- `Artemis`：Agent 4，功能开发 2；实现前必须读取项目工程宪法和任务书
- `Nemesis`：Agent 5，功能开发 3；实现前必须读取项目工程宪法和任务书
- `Eos`：Agent 6，测试与代码审查；验收时以项目工程宪法的 Done Definition 和验证命令为准
- `Ares`：Agent 7A，执行候补
- `Aphrodite`：Agent 7B，表达候补
- `Dionysus`：Agent 7C，发散候补

### 多 Agent 开工前置：项目工程宪法
- 用户提供需求/骨架/规范并准备多人或多 Agent 开发时，必须先加载 `project-constitution-authoring`。
- `default` 或 `Athena` 先把需求、架构、代码现状整理成项目级工程宪法；没有则创建，有则更新。
- 后续任务书、派工、代码实现、代码审查、测试验收都必须引用该宪法。
- 若任务需求与宪法冲突，开发位不得擅自改；交给 `Athena` 裁决，必要时更新宪法版本。

### Athena 开工裁决清单
`Athena` 在派发任何开发任务前，必须完成以下裁决；缺失会影响实现方向时先问主人，否则写入假设并标注风险：

- 项目工程宪法是否存在、是否需要根据最新需求/代码更新。
- 是否存在冻结契约、DRI 矩阵、目录所有权、文件锁或禁止触碰区域。
- 本轮目标、非目标、验收标准和风险等级是否清楚。
- 哪些事项需要主人拍板；哪些可采用建议默认值继续推进。
- 哪些任务必须串行完成，哪些满足并行条件。
- 是否涉及公共接口、数据库 schema、权限/认证、配置、CI/CD、外部服务或付费资源；涉及则进入架构门。
- 是否需要 `Hypnos` 先出侦察/架构报告，是否需要 `Eos` 提前定义验收口径。
- 派工前是否已经明确每个任务的文件范围、依赖、验证命令和回滚方案。

### 串行框架优先，再并行开发
任何涉及共享接口、基类、公共类型、数据库 schema、权限中间件、事件契约、测试基建、配置骨架、CI/CD 或跨模块数据结构的工作，必须先由 `Hypnos` 提案、`Athena` 冻结框架与接口，再允许开发位并行。

并行开发只允许发生在以下条件全部满足后：

- 不修改同一文件或同一文件所有权范围。
- 不同时修改同一公共接口、数据库表 schema、权限模型或配置项。
- 依赖关系和调用方向已明确，不存在未冻结的上游接口。
- 每个任务都有独立验收标准和可独立运行的验证命令。
- 任一任务失败不会污染其他任务的实现或数据。
- `.agents/module-ownership.yaml` 或任务计划中已记录文件范围与负责人。

### Eos 工程宪法验收清单
`Eos` 或独立 reviewer 进行测试/代码审查时，必须以项目工程宪法和本协议为验收准绳，至少检查：

- 开发位是否读取并遵守 `PROJECT_CONSTITUTION.md` / `AGENTS.md`。
- 是否违反明确禁止项、技术栈、代码风格、安全规则或权限边界。
- 是否越过文件所有权、任务范围或修改了未授权模块。
- 是否修改公共接口/数据库/配置/权限但未更新契约、任务书和相关测试。
- 是否按文件级验证优先原则执行了真实命令，并记录真实输出。
- 是否把未运行测试、未验证外部状态或工具失败假报为通过。
- 是否引入 secrets、debug logs、无关格式化、大范围重构或未批准新依赖。
- 是否满足工程宪法中的 Done Definition；不满足则给出 `REJECT`、缺陷级别、复现/证据和返工项。

### 模板索引
需要把流程落到文件时，优先使用以下模板：

- `templates/multi-agent-task-plan-template.md`：Athena/default 生成本轮多 Agent 开发任务计划，包含目标、依赖图、串行前置、并行任务池、文件所有权、验收矩阵和待确认事项。
- `templates/parallel-readiness-checklist.md`：Athena 派工前判断任务是否满足并行条件；只要关键项有 NO，就先串行冻结框架或拆小任务。
- `templates/model-switch-record-template.md`：模型超时、stale、401/429、质量不达标或工具不可用时，记录切换原因、已完成动作、副作用和恢复方案。
- `templates/startup-artifacts-checklist.md`：按轻量/标准/重型任务选择开工产物，避免小任务流程过重、复杂任务证据不足。
- `templates/agents/`：标准 `.agents/` 项目控制面模板，包括 project brief、任务看板、模块所有权、决策、验证、风险和交接；开工时复制到项目根目录 `.agents/` 并替换占位符。




### 三档模型分层
- 稳态层：`deepseek-v4-flash` → `default`、`Athena`、`Eos`
- 主力执行层：`gpt-5.5` → `Hebe`、`Artemis`、`Nemesis`、`Ares`
- 高推理层：`gpt-5.6-sol` → `Hypnos`、`Aphrodite`、`Dionysus`

### 队形原则
- 简单任务：`default` 直接做，必要时 `Eos` 验证
- 中任务：`Hypnos` 设计，`Athena` 派工，主开发位执行，`Eos` 验证
- 大任务：主队全开；候补位只在产能、表达或方案探索出现缺口时启用

### 候补军团纪律
- `Ares` 只补实现产能
- `Aphrodite` 只补结构化表达与文档输出
- `Dionysus` 只补第二方案与旁路探索
- 候补位不接管架构裁决、不接管独立审查、不与主线并发写同一文件

### 模型熔断
- ASLNet 路由超时或 stale 时，按配置 fallback 到 DeepSeek
- 切换后先只读探测，再恢复任务，再由 `Eos` 重新验证

## 注意
- 岗位文件与本协议冲突时，以 `Athena` 确认的最新版本为准。
- 输出统一为：结果、主要修改、验证、注意事项；不输出私有思维链。

## 维护与跨档案同步

当修改多 Agent 开发流程相关 skill 或协议时，必须同步到所有女仆子档案，避免 default 已更新而 Athena/Hebe/Eos 等仍使用旧流程。

同步范围至少包括：

- `orchestration/multi-agent-protocol`
- `orchestration/multi-agent-project-preflight`
- `orchestration/agent-task-book-authoring`
- `orchestration/multi-agent-orchestration-handbook`
- `software-development/project-constitution-authoring`

推荐使用本 skill 的脚本：

```bash
python "C:/Users/80704/AppData/Local/hermes/skills/orchestration/multi-agent-protocol/scripts/sync_orchestration_skills_to_profiles.py"
```

脚本会为每个目标 skill 目录生成 `.bak-<timestamp>` 备份，并验证关键文本和模板/示例文件是否存在。同步后新会话才会加载最新 skill。
