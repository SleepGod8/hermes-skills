# 审查 Findings 结构化与置信度校准规范（v1.9）

> 协议 v1.9 增量章节。来源：借鉴 garrytan/gstack 的 review-specialist 机制（结构化 finding + 置信度校准 + 红队对抗 + Pre-emit verification gate + 两遍分层审查 + 审查军团），用于解决 Agent 6 审查「误报多、结论不可追踪、各 Agent 输出格式不一」的实战痛点。
> 全团队必须遵从；与 enhanced-pipeline / multi-agent-protocol 冲突时，以本档案为准（与 workflow-retro-2026-08.md 同级增量）。

## 1. 背景与目标

现有 G5 审查流程（enhanced-pipeline 第 7 节）只规定了「验证顺序」和「P0-P3 缺陷等级」，但**没有规定 finding 怎么输出、怎么控制误报、怎么跨轮次追踪**。实际后果：

- 低置信度的「可能有问题」和高置信度的「确定有 bug」混在一起，Agent 1 无法判断先处理哪个。
- 同一个缺陷被不同 Agent 反复报、换句话报，无法去重。
- 审查报告是自由文本，无法沉淀进 task-board / test-reports 做可复查证据。

本规范补齐：**统一 finding 结构 + 强制置信度 + 分级显示 + 显式空结果**。

## 2. 审查执行顺序：两遍分层（Pass 1 / Pass 2）

Agent 6 审查必须分两遍执行，**先扫致命类、再扫常规类**，不得一次性混扫：

### 2.1 Pass 1（CRITICAL）：致命类

第一遍只聚焦致命类别，发现任一 CRITICAL 即有权给出 `BLOCKED`，不必扫完 Pass 2：

| 致命类 | 说明 |
|--------|------|
| SQL / 数据安全 | 注入、越权读写、数据损坏 |
| LLM 输出信任边界 | AI 生成的代码是否盲目信任 LLM/外部输出（未校验即使用） |
| 认证 / 权限 / 支付 | 鉴权绕过、越权、支付逻辑错误 |
| 不可逆操作 | 删除 / 迁移 / 权限变更 无回滚或未审批 |

### 2.2 Pass 2（其余）：常规类

Pass 1 通过（或无 CRITICAL）后，再扫其余所有 specialist 视角：security 其余、performance、testing、maintainability、api-contract、data-migration、red-team。

### 2.3 与 verification gate 及汇总的衔接

- Pass 1 的 finding **强制过 verification gate**（逐字引用触发原文），拿不出代码行原文的 CRITICAL 同样压进附录——致命类更要卡死证据门槛。
- Pass 1 发现 CRITICAL → 直接 `BLOCKED`，Pass 2 可暂停，等 Agent 1 裁决是否继续。
- 两遍结果按「汇总报告模板」聚合，Pass 1 / Pass 2 分节呈现。

## 3. 结构化 Finding 格式（统一 JSON）

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

### 3.1 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `fingerprint` | ✅ | `文件:行号:category` 唯一标识，用于**去重、跨轮次追踪、判断是否已修复** |
| `severity` | ✅ | 缺陷等级，**沿用现有 P0-P3**（P0 阻断发布 / P1 必须修复 / P2 当前任务修复 / P3 记录后续） |
| `confidence` | ✅ | 置信度 1-10（见第 4 节） |
| `specialist` | ✅ | 专家视角，取值见第 7 节枚举 |
| `path` / `line` | 条件 | 有明确位置的必填；无位置（如架构级问题）可省略 line |
| `category` | ✅ | 缺陷类别（security / performance / testing / data-migration / maintainability / api-contract / red-team） |
| `summary` | ✅ | 一句话说清问题 |
| `evidence` | ✅ | **强制证据门槛（v1.7）**：必须逐字引用触发问题的原文——具体缺陷引用代码行（`file:line` + 原文），架构级问题引用设计文档/契约/ADR 原文，跨文件问题引用两个触发点原文。引不出原文 = 未验证，按 4.2 降级 |
| `fix` | ✅ | 修复建议（可简，但必须有） |

### 3.2 fingerprint 规则

- 同一 `文件:行号:类别` 视为同一条 finding，重复出现只保留一条，**更新而不新增**。
- 修复后再次审查，该 fingerprint 消失 = 确认已解决，可写进复盘。
- 行号漂移（代码改动导致行号变化）时，允许以 `文件:类别:summary 前 N 字` 作为弱 fingerprint，避免误判为「新缺陷」。

## 4. 置信度校准（Confidence Calibration）

`confidence` = 该 finding 是**真实缺陷**的把握程度（1-10），不是「重要性」，重要性由 severity 表达。

### 4.1 评分锚点

| 分数 | 含义 | 判据 |
|------|------|------|
| 9-10 | 可立即断定 | 有测试失败 / 复现输出 / 确凿代码证据 |
| 7-8 | 强证据 | 静态检查命中 + 代码上下文明确 |
| 5-6 | 可疑待核实 | 可能是误报，需人工复核 |
| 3-4 | 弱信号 | 风格问题 / 泛化模式 / 猜测 |
| 1-2 | 无实质依据 | 直觉 / 待确认，禁止作为结论 |

### 4.2 强制降级规则

1. **无 `evidence` 字段的 finding，confidence 上限 = 4**（没有证据就不是强结论）。
2. 措辞含「可能 / 似乎 / 建议检查一下 / 不确定」的 finding，confidence 默认 ≤5。
3. 单纯「不符合最佳实践」而无实际影响路径的，confidence 默认 ≤4，severity 默认 P3。
4. 不允许为了凑 finding 数量而放宽置信度或制造低置信度噪音。
5. **Pre-emit verification gate（v1.7 新增，硬门槛）**：任何 finding 提升进报告前，必须能逐字引用触发它的原文（代码行 / 设计文档 / 契约）。引不出原文 → 视为未验证 → 强制 confidence ≤5 → 抑制出主报告，仅进附录供审计校准；不得靠编造 speculative confidence 7+ 绕过此门槛。
6. **Framework-meta nudge（v1.7 新增）**：当符号由框架元类/ORM 生成（Django `Meta`、SQLAlchemy `relationship`/`Column`、TypeORM 装饰器、Prisma 生成 client、Rails `has_many` 等），必须先引用那个 meta-construct 原文，**不得武断报「字段不存在」**——避免误杀框架魔术方法。

## 5. 分级显示规则（控误报、防刷屏）

审查报告按 confidence 分级呈现，低置信度不占主报告：

| confidence | 处理 |
|------------|------|
| 9-10 | 进入主报告，正常显示 |
| 7-8 | 进入主报告，标注「建议复核」 |
| 5-6 | 归入「待核实」区，附 caveat |
| 3-4 | 压到附录（低优先级），不占主报告 |
| 1-2 | 仅当无任何 P0/P1 或 Agent 1 明确要求时才报告 |

> 目标：Agent 1 打开审查报告，第一屏只看到「高置信度 + 必须处理」的硬问题，不被低置信度噪音淹没。低置信度条目**保留在附录**，不删除，作为可复查记录。

## 6. 汇总报告模板

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

## 7. Specialist 枚举与视角

审查可拆分为多专家视角，**全部由 Agent 6（测试审查岗）内部轮转**，每个 finding 声明 `specialist`：

| specialist | 关注点 | 承担岗位 |
|------------|--------|----------|
| `security` | 注入、越权、路径、反序列化、密钥泄漏 | Agent 6 |
| `red-team` | **对抗式**：攻击者 / 混沌工程 / 敌意 QA，专找其他视角漏掉的 | Agent 6 |
| `performance` | 复杂度、热点、资源泄漏、慢查询 | Agent 6 |
| `testing` | 测试覆盖缺口、可测试性、断言质量 | Agent 6 |
| `api-contract` | 接口契约一致性、破坏性变更 | Agent 6 审，Agent 2 供契约 |
| `data-migration` | 迁移顺序、回填、兼容、回滚 | Agent 6 审，Agent 2 供迁移方案 |
| `maintainability` | 可读性、重复、技术债 | Agent 6 |

### 7.1 红队视角（Agent 6 对抗式）

`red-team` **不是检查清单，是对抗式分析**：明确假设「这是要上生产、会有恶意输入和并发故障的代码」，主动构造攻击/破坏场景找漏洞，输出其他 specialist 漏掉的 finding。红队 finding 的 `category` 用 `red-team`，`evidence` 必须是「具体可复现的攻击/失败路径」，否则按 4.2 强制降级。

**岗位独立性（硬约束）**：红队是审查职能，只归 Agent 6（测试审查岗），**不得与任何开发岗（Agent 3/4/5）或项目负责人（Agent 1）兼任**——审查者不能审查自己参与实现的代码，否则对抗价值作废。各女仆的人格语气（毒舌/冷静等）仅用于日常聊天，**不作为审查岗位依据**。

## 8. 审查军团（review-army）

默认由 Agent 6 单人轮转第 7 节全部 specialist 视角；仅当审查量超出单人能力时，Agent 1 可临时组建「审查军团」并行审查。

### 8.1 触发条件

| 条件 | 说明 |
|------|------|
| 大型跨模块重构 | diff > 500 行，或跨 >5 个文件 |
| 高风险领域 | 公共 API、数据库迁移、认证 / 支付 |
| Agent 1 判断单审不够 | 单人审查发现 CRITICAL 密集，需多视角复核 |

### 8.2 组成（岗位独立性红线）

- **主导 + 汇总**：Agent 6（测试审查岗）—— 出最终结论，唯一有权给 PASS / BLOCKED。
- **补位审查者**：候补岗（`soul-00-standby`）在 Agent 1 分派下临时领审查任务。
- **禁止参与**：开发岗（Agent 3/4/5）、项目负责人（Agent 1）、架构（Agent 2）不碰审查。

### 8.3 视角分配 = 任务级临时分派（不改岗位）

候补女仆的岗位**保持 standby 不变**，审查视角由 Agent 1 在 task-board 的任务契约里临时指定，属「任务级分派」而非「岗位级职责」：

1. Agent 1 登记：启用原因、任务编号、每人视角、文件范围、验收标准、预计结束条件、交接对象（呼应 Agent 7 候补机制）。
2. 视角示例（每次可换，**不固定绑定**）：
   - ares → `performance`（复杂度 / 热点 / 资源泄漏）
   - aphrodite → `maintainability`（可读性 / 重复 / 技术债）
   - dionysus → `security`（注入 / 越权 / 密钥）
3. 补位者只交 finding，不越权给结论；任务完成即回 standby。

### 8.4 交叉验证（多审查者独立证实加权）

- ≥2 个审查者独立报告同源 finding → confidence **+1**（cap 10），标注「独立证实」。
- 单一来源 → 维持原 confidence。
- **交叉验证不得突破 verification gate**：多人都报「字段不存在」但都引用不出代码行原文，仍是未验证，压附录（三人同幻觉 ≠ 事实）。

### 8.5 岗位独立性硬约束

1. 补位审查者只能是候补岗（standby），开发岗 / 负责人不碰审查。
2. 补位者不得审查自己参与开发的模块。
3. 最终结论只由 Agent 6 出，补位者只交 finding。

## 9. 空结果与反模式

### 9.1 空结果显式声明

审查无问题时，输出 `NO FINDINGS`（或 `NO P0/P1`），不允许为了「显得认真」硬造低置信度 finding。空结果本身是有效结论。

### 9.2 反模式（禁止）

- 把「可能有问题」当成「确定有 bug」写进主报告（违反置信度分级）。
- 同一缺陷换措辞重复报（违反 fingerprint 去重）。
- 用自由文本描述 finding，不落 JSON（无法沉淀进 test-reports）。
- 无证据但给高置信度（违反 4.2）。
- 红队视角变成复述安全清单（违反 7.1 对抗式原则）。

## 10. 与现有流程衔接

- G5 审查结论（PASS / CHANGES_REQUESTED / BLOCKED / REJECTED）**不变**。
- 缺陷等级 P0-P3 **不变**，映射到 finding 的 `severity` 字段。
- 审查报告 = 第 5 节汇总模板 + 完整 JSON 行列表，**落盘到 `.agents/test-reports/`**，作为可复查证据（呼应「证据优先」「汇报必须附可复查产物」）。
- 第 2-9 节是 G5 的增量要求，其他 G0-G7 流程不动。

## 11. 落地检查清单（Agent 6 每次审查前）

- [ ] 是否按两遍分层（Pass 1 致命 / Pass 2 常规）执行？
- [ ] 每条 finding 是否都有 fingerprint + confidence + evidence？
- [ ] confidence 是否遵守评分锚点和强制降级规则？
- [ ] 是否按 confidence 分级呈现（高置信度进主报告，低置信度进附录）？
- [ ] 是否输出汇总模板 + 完整 JSON 行列表？
- [ ] 空结果是否显式声明 NO FINDINGS？
- [ ] 红队视角是否做到了对抗式（而非复述清单）？
- [ ] 每条 finding 是否逐字引用了触发原文（verification gate）？
- [ ] 审查报告是否落盘 `.agents/test-reports/`？
- [ ] （Agent 1）审查量大时是否按「审查军团」规范组建并行审查，而非单人硬扛？
