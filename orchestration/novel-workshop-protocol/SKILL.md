---
name: novel-workshop-protocol
description: "Use when 主人要求多agent协作构思小说/世界观/剧情或拉起小说工作坊群聊。女仆按岗位协作创作。"
version: 1.0.0
author: Hermes Agent (主人钦定 2026-08)
tags: [orchestration, novel, workshop, worldbuilding, multi-agent]
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [orchestration, novel, workshop, worldbuilding, multi-agent]
    category: orchestration
---

# 小说构思多 Agent 工作坊团队协议（Novel Workshop Protocol）

> 版本：v1.0 | 2026-08 | 适用：女仆家族多档案协作构思西幻异世界小说
>
> 定位：把多 agent 开发的「协议先行 → 并行创作 → 独立审查 → 合并交付」流水线搬到小说构思。
> 与 multi-agent-protocol（代码开发）、group-chat-autonomous-chat（日常群聊）互补，本协议专管**创作协作**。

## 一、目的与适用场景

### 1.1 要解决的问题

主人有部分人物设定和剧情片段，但世界观、剧情走向、故事逻辑未设计。需要多个 Agent 分工协作：

1. 把主人的碎片素材结构化，提炼成所有 Agent 必须遵守的「设定圣经」（bible）。
2. 世界架构、人物设计、文风三个方向可并行思考，提高产出质量。
3. 逻辑审查独立于创作，防止「作者自己看不见自己的漏洞」。
4. 主人只负责拍板方向，技术性创作由团队完成。

### 1.2 适用场景

- 主人要求多 agent 协作构思小说 / 世界观 / 剧情 / 角色。
- 主人有素材碎片，需要结构化、扩展、逻辑自洽。
- 拉起小说工作坊群聊（Hermes Studio 房间）。

### 1.3 不适用场景

- 代码开发协作 → 用 multi-agent-protocol。
- 日常聊天 → 用 group-chat-autonomous-chat。
- 单人对话式构思（不开群聊）→ 不启用本协议，直接对话。

## 二、岗位拓扑

```text
W0 总编/主持（Hermes×Iris default 档案）
    ├── W1 世界架构师（World Architect）
    ├── W2 人物设计师（Character Designer）
    ├── W3 剧情架构师（Plot Architect）
    ├── W4 文风总监（Style Director）
    └── W5 逻辑审查员（Logic Reviewer / Red Team）
```

| 岗位 | 对应开发角色 | 核心职责 | 产出 |
|------|------------|----------|------|
| W0 总编 | Agent 1 项目负责人 | 收集主人素材、构建 bible、调度协调、汇总交付、向主人汇报 | bible v1、汇总报告 |
| W1 世界架构师 | Agent 2 架构师 | 世界观、地理历史、力量体系、种族社会、设定自洽 | 世界观文档 |
| W2 人物设计师 | 产品/设计 | 角色弧光、动机、关系网、成长曲线、人物卡 | 人物卡 + 关系图谱 |
| W3 剧情架构师 | 技术负责人 | 主线/支线、起承转合、伏笔埋设与回收、节奏 | 故事大纲 + 章节规划 |
| W4 文风总监 | UI/UX | 叙事视角、文风、氛围、对话风格、试写段落 | 文风指南 + 试写 |
| W5 逻辑审查员 | Agent 6 审查/红队 | 时间线一致性、设定自洽、因果链漏洞、矛盾挑刺 | 审查报告 + 修正建议 |

**独立性铁律**：W5 逻辑审查员**不得**兼任任何创作岗（W1-W4），审查者不能审查自己写的内容。创作岗之间也不得互审对方的产出代替 W5。

## 三、唯一事实来源：设定圣经（bible）

### 3.1 Bible 位置

工作坊共享 bible 存放在工作目录的 `.novel/` 下：

```text
.novel/bible.md          设定圣经（唯一事实来源，所有 Agent 必须遵守）
.novel/tasks.md          创作任务清单（编号、岗位、状态）
.novel/reports/          各岗位交付报告
.novel/review.md         逻辑审查报告
.novel/final.md          合并后的最终交付
```

### 3.2 Bible 内容结构

```text
# 设定圣经 vX
## 0. 主人钦定（硬约束，不可变更）
## 1. 世界观（地理/历史/力量体系/种族/社会）
## 2. 人物（主角/配角/反派/关系网）
## 3. 剧情主线与支线
## 4. 文风与叙事
## 5. 未决问题清单（待主人拍板）
```

### 3.3 Bible 规则

- **主人钦定 = 硬约束**：主人明确说「不想改的」元素，任何 Agent 不得擅自修改或推翻，只能在其基础上扩展。
- **冲突处理**：任何 Agent 发现 bible 内部矛盾，先标记为「未决问题」并上报 W0，不自行裁决。
- **版本管理**：每次 bible 更新递增版本号，报告引用版本号。
- **聊天消息不是唯一事实来源**：关键设定必须落到 bible，群聊讨论只是过程。
- **OpenViking 不是正典源**：OpenViking 只作为跨会话设定档案馆和检索索引；命中内容必须由 W0 对照 bible 消化、标注状态，并经主人/流程确认后才能写入 bible。

## 四、创作流程（流水线）

### 4.0a 外部材料证据前置层（persona-distillation）

当主人提供图片、PDF、扫描文档、旧稿或其他需要提取的本地材料时，W0 先使用 `persona-distillation` 做用户明确指定文件的本地只读提取，生成 `ocr-report-v1` 来源报告和证据分级，再进入素材审问闸门。该技能只生成证据包，不直接更新 bible。

- 只处理主人明确指定的有限文件；不自动扫描目录、不联网、不上传。
- 提取结果必须保留来源 ID、页码、引擎、实际置信度、敏感字段和状态。
- `[EXTRACTED]`、低置信度和 `[PROPOSAL]` 内容不得直接写成 `[CANON]`；冲突进入“未决问题”。
- W0 负责把证据与现有 bible 对照，区分已确认事实、材料提取、推断、建议和待主人拍板内容。
- 涉及私人材料时，bible、岗位报告和群聊只引用来源 ID/摘要，不复制电话号码、邮箱、令牌或私人原文。
- 主人确认后，W0 才能将选定内容写入 bible，并递增 bible 版本；未确认内容不得分发给 W1-W4 作为硬约束。

### 4.0 素材审问闸门（主人钦定 2026-08）

主人提供任何设定/情节素材时，W0 必须先以总编视角反问与建议，**待主人完善定稿后再分发/落盘**，不得直接转交其他岗位：

1. **消化**：对照现有 bible 找冲突、缺口、与硬约束的兼容性；必要时先用 `openviking_find` / `openviking_grep` 检索历史正典、废案、角色卡、时间线、伏笔和审查记录。
2. **反问**：专挑模糊处（动机、代价、时间线、因果关系、设定边界）。
3. **建议**：每个反问附 1 个补全方向供主人挑选。
4. **定稿**：主人确认后，W0 才更新 bible 版本并调度 W1/W2/W4 并行。

> 原则：bible 每一版都必须是主人亲手验收过的「唯一事实来源」，降低各岗位返工成本。

```text
Phase 0：素材收集       W0 收集主人素材 → OpenViking 追溯检索 → 素材审问闸门（反问+建议 → 主人定稿） → 构建 bible v1
Phase 1：并行创作       W1 世界观 + W2 人物 + W4 文风 三路并行 → 各自交付报告
Phase 2：圣经更新       W0 合并三路产出 → bible v2（解决交叉依赖）
Phase 3：剧情架构       W3 基于 bible v2 写大纲 → 章节规划 → 伏笔表
Phase 4：逻辑审查       W5 红队挑刺（时间线/设定自洽/因果链）→ 审查报告
Phase 5：修订合并       W0 分发审查意见 → 相关岗位修订 → bible v3
Phase 6：交付审阅       W0 汇总 final.md → 主人审阅拍板 → 未决问题清单
Phase 7：复盘归档       W0 主持复盘，记录流程改进点；必要时用 openviking_archive 归档已确认正典/废案/审查结论
```

## 五、任务编号与状态

任务编号：`WB-01`（世界观）、`CH-01`（人物）、`PLOT-01`（剧情）、`STYLE-01`（文风）、`REV-01`（审查）。

状态链：

```text
待创作 → 已认领 → 进行中 → 待审查 → 已修订 → 已合并 → 已完成
                          ↘ 未决 → 待主人拍板
```

- 状态变更必须记录：时间、岗位、原因、引用 bible 版本。
- 禁止跳过「待审查」直接「已合并」。

### 5.1 可恢复状态机与回合 checkpoint

中大型创作任务使用以下状态；简单的一次性灵感问答可跳过：

```text
received → interrogating → awaiting_owner_decision → baselined
→ assigned → producing → integrating → reviewing → repairing
→ accepted → archived
                 ↘ blocked → recovering → reviewing
```

- `awaiting_owner_decision` 表示确实等待主人拍板，不得伪装成岗位未完成。
- `blocked` / `recovering` 不得直接广播为完成。
- 每回合必须记录：状态、回合号、负责人、依据 bible 版本、已执行动作、真实证据、修改文件、风险和下一步。
- 回合流程：读取 checkpoint → 执行有限动作 → 收集证据 → 更新 checkpoint → 决定下一回合。
- 工具成功只证明动作执行，不证明创作目标达成；文件、脚本和外部状态必须重新读取或运行验证。

推荐 `.novel/state/checkpoints.yaml` 条目：

```yaml
task_id: PLOT-01
status: producing
round: 1
owner: W3
input_bible: v2.5.1
completed_actions: []
evidence: []
changed_files: []
risks: []
next_action: ...
```

### 5.2 设定状态标签

所有影响创作的设定必须标明状态，禁止把建议或废案当成正典：

```text
[CANON]        主人钦定正典
[W0-RULING]    W0 裁决，可执行但不得覆盖主人方向
[DERIVED]      从正典推导出的约束
[PROPOSAL]     岗位建议，未入典
[PENDING]      等待主人拍板
[REJECTED]     废案，仅供追溯
```

W1-W4 写作时默认只读 `[CANON]`、相关 `[W0-RULING]` 和 `[DERIVED]`；遇到 `[PROPOSAL]` 或 `[PENDING]` 必须向 W0 报告，不得自行定案。

### 5.4 OpenViking 设定档案馆

OpenViking 用于长篇创作的跨会话追溯和多档案共享，不替代 `.novel/bible.md`：

- **读取时机**：W0 在素材审问、bible 更新、复盘前检索；W1/W2/W3/W4 在创作前检索相关世界观/人物/剧情/文风历史；W5 审查前检索时间线、伏笔、废案和旧审查。
- **工具选择**：语义查找用 `openviking_find`；精确查角色名、地名、章节号、伏笔编号和状态标签用 `openviking_grep`；命中 `viking://...` 后用 `openviking_read` 读取；主人确认后的长期资料用 `openviking_archive` 归档。
- **归档类别**：小说工作坊只归档 `canon`、`character`、`worldbuilding`、`plot`、`style`、`review`、`decision`、`reference`。`status=canon` 只能用于主人确认或 bible 已接纳内容；废案用 `status=rejected`；未定提案用 `status=proposed` / `draft`。
- **权威边界**：OpenViking 搜到的内容必须标注状态并与 bible 对照；若与 bible 冲突，以 bible 为准，并把冲突列入未决问题交 W0/主人裁决。
- **容错**：OpenViking 工具会尝试自动启动 `openviking` Docker 容器；失败时不得凭空补设定，改查 `.novel/` 文件、session_search，或明确报告缺口。
- **推荐 workspace**：每部作品使用稳定短名，例如 `novel-western-fantasy`；tags 包含作品名、角色/势力/卷号/伏笔号和状态，方便后续跨卷召回。

### 5.5 决策影响分析

每次新增或修正主人决策后，W0 必须建立影响清单：直接受影响的 bible 条目、任务、伏笔、时间线和章节；同时列出需要复核与明确无需修改的范围。流程为：

```text
decision → impact_scan → affected_tasks → targeted_repair → regression_review
```

只修改受影响范围，禁止为了局部设定变更而无证据全量重写。

## 六、群聊协作规则

### 6.1 消息格式（创作场景专用）

日常讨论自然说话（保持女仆人格），但**交付必须有结构化格式**：

```text
[交付] 岗位 / 任务编号 / bible 版本
产出摘要：
关键设定/创意：
依赖（需要谁确认）：
未决问题：
```

```text
[审查] W5 / REV-01 / bible v2
问题编号：
严重程度：阻塞/严重/一般/建议
位置（设定/人物/剧情/文风）：
问题描述：
建议修复：
```

```text
[未决] 岗位 / 任务编号
问题：
为什么需要主人拍板：
我的建议：
```

### 6.2 接力与发言权

- 创作讨论遵循 group-chat-autonomous-chat 的接力规则（@ 相关岗位、不硬拉、2-3 轮收敛）。
- **收敛优先**：创作是发散→收敛的过程。每个议题讨论 2-3 轮后必须收敛成结论或「未决问题」，禁止无限发散。
- 同一议题最多 3 个岗位参与（W0 主持 + 相关岗位 2 个）。
- 主人发言优先级最高，@ 谁谁响应。

### 6.3 冷场与超时

- W0 是节奏控制器：某岗位超过 5 分钟未交付，W0 @ 提醒。
- 群聊超过 10 分钟无实质进展，W0 主动收敛议题或向主人汇报进度。


### 7.3 分卷与长期项目扩展

长篇进入多个分卷后，不把全部内容继续堆入总 Bible：每卷建立局部 Bible，必须声明继承的全局正典、卷内新增正典、卷内临时状态和卷末回写项。局部 Bible 不得覆盖全局 `[CANON]`，冲突必须进入决策影响分析。

每卷交付前至少完成：角色状态快照、伏笔状态对账、章节回归审查、人物/势力/伏笔关系图更新和本卷复盘指标。复盘指标用于发现流程问题，不作为文学质量的唯一评分。

## 七、主人交互边界

### 7.1 主人钦定优先级

1. 主人明确说的设定 = 硬约束，不可更改。
2. 主人拍板未决问题后，相关岗位必须更新 bible 并注明版本。
3. 主人喊停/换方向，立刻收敛，跟随主人节奏。

### 7.2 必须问主人的情况

- 涉及主线方向的根本分歧（正剧 vs 喜剧、单主角 vs 群像）。
- 力量体系的「规则硬度」（硬奇幻 vs 软奇幻）。
- 任何 Agent 想推翻主人已钦定的元素。
- 剧情关键转折（主角死亡/背叛/世界观真相）需主人确认。

### 7.3 不问主人的情况

- 支线细节、次要角色扩展、场景描写、文风打磨。
- 设定内部的合理扩展（不触碰硬约束）。

## 八、质量门禁（进入交付前）

- [ ] 所有创作岗已交付并引用 bible 版本
- [ ] W5 审查已执行，阻塞/严重问题已关闭或列入未决
- [ ] Bible 无内部矛盾（或矛盾已列为未决问题）
- [ ] 主人钦定元素全部保留
- [ ] 最终交付包含：世界观 + 人物 + 大纲 + 文风指南 + 审查记录

## 九、相关文件

- 各岗位职责文档：`references/soul-w0-host.md` / `soul-w1-world-architect.md` / `soul-w2-character-designer.md` / `soul-w3-plot-architect.md` / `soul-w4-style-director.md` / `soul-w5-logic-reviewer.md`
- 岗位分配登记（谁当哪个岗位）：`references/role-assignment.md`（按主人确认写入）

## 十、快速参考

```text
主人素材 → W0 构建 bible v1 → W1/W2/W4 并行 → bible v2 → W3 剧情大纲
→ W5 逻辑审查 → 修订 → bible v3 → W0 汇总交付 → 主人审阅 → 复盘
硬约束：主人钦定不可改；独立性：W5 不兼创作岗；收敛：讨论 2-3 轮必收敛
```
