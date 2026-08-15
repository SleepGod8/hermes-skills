# 审查 Findings 结构化与置信度校准规范（v1.6）

> 协议 v1.6 增量章节。来源：借鉴 garrytan/gstack 的 review-specialist 机制（结构化 finding + 置信度校准 + 红队对抗），用于解决 Agent 6 审查「误报多、结论不可追踪、各 Agent 输出格式不一」的实战痛点。
> 全团队必须遵从；与 enhanced-pipeline / multi-agent-protocol 冲突时，以本档案为准（与 workflow-retro-2026-08.md 同级增量）。

## 1. 背景与目标

现有 G5 审查流程（enhanced-pipeline 第 7 节）只规定了「验证顺序」和「P0-P3 缺陷等级」，但**没有规定 finding 怎么输出、怎么控制误报、怎么跨轮次追踪**。实际后果：

- 低置信度的「可能有问题」和高置信度的「确定有 bug」混在一起，Agent 1 无法判断先处理哪个。
- 同一个缺陷被不同 Agent 反复报、换句话报，无法去重。
- 审查报告是自由文本，无法沉淀进 task-board / test-reports 做可复查证据。

本规范补齐：**统一 finding 结构 + 强制置信度 + 分级显示 + 显式空结果**。

## 2. 结构化 Finding 格式（统一 JSON）

Agent 6 审查产出的每一条缺陷，必须输出为一行结构化记录（JSON），不允许自由文本：

```json
{
  "fingerprint": "src/module_a.py:42:security",
  "severity": "P1",
  "confidence": 8,
  "specialist": "security",
  "path": "src/module_a.py",
  "line": 42,
  "category": "security",
  "summary": "SQL 字符串拼接，存在注入风险",
  "evidence": "grep 命中 `f\"SELECT * FROM t WHERE id={uid}\"`，未走参数化",
  "fix": "改用参数化查询 / ORM"
}
```

### 2.1 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `fingerprint` | ✅ | `文件:行号:category` 唯一标识，用于**去重、跨轮次追踪、判断是否已修复** |
| `severity` | ✅ | 缺陷等级，**沿用现有 P0-P3**（P0 阻断发布 / P1 必须修复 / P2 当前任务修复 / P3 记录后续） |
| `confidence` | ✅ | 置信度 1-10（见第 3 节） |
| `specialist` | ✅ | 专家视角，取值见第 6 节枚举 |
| `path` / `line` | 条件 | 有明确位置的必填；无位置（如架构级问题）可省略 line |
| `category` | ✅ | 缺陷类别（security / performance / testing / data-migration / maintainability / api-contract / red-team） |
| `summary` | ✅ | 一句话说清问题 |
| `evidence` | ✅ | **证据优先**（呼应 enhanced-pipeline 原则 2）：命令、退出码、代码片段、复现步骤；无证据见 3.2 强制降级 |
| `fix` | ✅ | 修复建议（可简，但必须有） |

### 2.2 fingerprint 规则

- 同一 `文件:行号:类别` 视为同一条 finding，重复出现只保留一条，**更新而不新增**。
- 修复后再次审查，该 fingerprint 消失 = 确认已解决，可写进复盘。
- 行号漂移（代码改动导致行号变化）时，允许以 `文件:类别:summary 前 N 字` 作为弱 fingerprint，避免误判为「新缺陷」。

## 3. 置信度校准（Confidence Calibration）

`confidence` = 该 finding 是**真实缺陷**的把握程度（1-10），不是「重要性」，重要性由 severity 表达。

### 3.1 评分锚点

| 分数 | 含义 | 判据 |
|------|------|------|
| 9-10 | 可立即断定 | 有测试失败 / 复现输出 / 确凿代码证据 |
| 7-8 | 强证据 | 静态检查命中 + 代码上下文明确 |
| 5-6 | 可疑待核实 | 可能是误报，需人工复核 |
| 3-4 | 弱信号 | 风格问题 / 泛化模式 / 猜测 |
| 1-2 | 无实质依据 | 直觉 / 待确认，禁止作为结论 |

### 3.2 强制降级规则

1. **无 `evidence` 字段的 finding，confidence 上限 = 4**（没有证据就不是强结论）。
2. 措辞含「可能 / 似乎 / 建议检查一下 / 不确定」的 finding，confidence 默认 ≤5。
3. 单纯「不符合最佳实践」而无实际影响路径的，confidence 默认 ≤4，severity 默认 P3。
4. 不允许为了凑 finding 数量而放宽置信度或制造低置信度噪音。

## 4. 分级显示规则（控误报、防刷屏）

审查报告按 confidence 分级呈现，低置信度不占主报告：

| confidence | 处理 |
|------------|------|
| 9-10 | 进入主报告，正常显示 |
| 7-8 | 进入主报告，标注「建议复核」 |
| 5-6 | 归入「待核实」区，附 caveat |
| 3-4 | 压到附录（低优先级），不占主报告 |
| 1-2 | 仅当无任何 P0/P1 或 Agent 1 明确要求时才报告 |

> 目标：Agent 1 打开审查报告，第一屏只看到「高置信度 + 必须处理」的硬问题，不被低置信度噪音淹没。低置信度条目**保留在附录**，不删除，作为可复查记录。

## 5. 汇总报告模板

Agent 6 审查结束时，先输出汇总，再附完整 JSON 行列表：

```text
审查结论：PASS / CHANGES_REQUESTED / BLOCKED / REJECTED
Finding 总数：N
  高置信度（≥7）：x 条 —— 必须处理
  中置信度（5-6）：y 条 —— 待核实
  低置信度（≤4）：z 条 —— 见附录
P0: a | P1: b | P2: c | P3: d
```

汇总表按 `severity × confidence` 聚合，便于 Agent 1 按「先高置信度 P0/P1，再往下」的优先级处理。

## 6. Specialist 枚举与视角

审查可拆分为多专家视角（一个 Agent 6 内部轮转，或按人设分工），每个 finding 声明 `specialist`：

| specialist | 关注点 | 建议岗位 |
|------------|--------|----------|
| `security` | 注入、越权、路径、反序列化、密钥泄漏 | Athena（冷静严谨） |
| `red-team` | **对抗式**：攻击者 / 混沌工程 / 敌意 QA，专找其他视角漏掉的 | Nemesis（毒舌雌小鬼，天然红队） |
| `performance` | 复杂度、热点、资源泄漏、慢查询 | Agent 6 通用 |
| `testing` | 测试覆盖缺口、可测试性、断言质量 | Agent 6 通用 |
| `api-contract` | 接口契约一致性、破坏性变更 | Agent 2 配合 |
| `data-migration` | 迁移顺序、回填、兼容、回滚 | Agent 2 配合 |
| `maintainability` | 可读性、重复、技术债 | Agent 6 通用 |

### 6.1 红队视角（Nemesis 岗位）

`red-team` **不是检查清单，是对抗式分析**：明确假设「这是要上生产、会有恶意输入和并发故障的代码」，主动构造攻击/破坏场景找漏洞，输出其他 specialist 漏掉的 finding。红队 finding 的 `category` 用 `red-team`，`evidence` 必须是「具体可复现的攻击/失败路径」，否则按 3.2 强制降级。

## 7. 空结果与反模式

### 7.1 空结果显式声明

审查无问题时，输出 `NO FINDINGS`（或 `NO P0/P1`），不允许为了「显得认真」硬造低置信度 finding。空结果本身是有效结论。

### 7.2 反模式（禁止）

- 把「可能有问题」当成「确定有 bug」写进主报告（违反置信度分级）。
- 同一缺陷换措辞重复报（违反 fingerprint 去重）。
- 用自由文本描述 finding，不落 JSON（无法沉淀进 test-reports）。
- 无证据但给高置信度（违反 3.2）。
- 红队视角变成复述安全清单（违反 6.1 对抗式原则）。

## 8. 与现有流程衔接

- G5 审查结论（PASS / CHANGES_REQUESTED / BLOCKED / REJECTED）**不变**。
- 缺陷等级 P0-P3 **不变**，映射到 finding 的 `severity` 字段。
- 审查报告 = 第 5 节汇总模板 + 完整 JSON 行列表，**落盘到 `.agents/test-reports/`**，作为可复查证据（呼应「证据优先」「汇报必须附可复查产物」）。
- 第 2-7 节是 G5 的增量要求，其他 G0-G7 流程不动。

## 9. 落地检查清单（Agent 6 每次审查前）

- [ ] 每条 finding 是否都有 fingerprint + confidence + evidence？
- [ ] confidence 是否遵守评分锚点和强制降级规则？
- [ ] 是否按 confidence 分级呈现（高置信度进主报告，低置信度进附录）？
- [ ] 是否输出汇总模板 + 完整 JSON 行列表？
- [ ] 空结果是否显式声明 NO FINDINGS？
- [ ] 红队视角是否做到了对抗式（而非复述清单）？
- [ ] 审查报告是否落盘 `.agents/test-reports/`？
