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

## 使用方式

当用户要求进行多 Agent 开发时：

1. 加载本技能，并读取 `references/` 下全部相关文件。
2. 先按固定编制选队形：`default` 总控中枢，`Athena/Hypnos/Hebe/Artemis/Nemesis/Eos` 为主队，`Ares/Aphrodite/Dionysus` 为候补军团。
3. 按协议执行：任务编号、状态机、标准消息格式、文件所有权、合并顺序、质量门禁。
4. 关键决定落到 `.agents/` 工件，不以聊天消息为唯一事实来源。

## 核心要点速查

### 固定编制
- `default`：总控中枢、会话协调、汇总输出
- `Athena`：Agent 1，项目负责人、集成与发布
- `Hypnos`：Agent 2，代码侦察与架构设计
- `Hebe`：Agent 3，功能开发 1
- `Artemis`：Agent 4，功能开发 2
- `Nemesis`：Agent 5，功能开发 3
- `Eos`：Agent 6，测试与代码审查
- `Ares`：Agent 7A，执行候补
- `Aphrodite`：Agent 7B，表达候补
- `Dionysus`：Agent 7C，发散候补

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
