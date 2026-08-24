---
name: project-doc-suite-authoring
description: "Use when 生成项目全套技术文档（需求/架构/API/数据库/测试/设计/开发指南）并保持跨文档契约一致。"
version: 1.0.0
tags: [documentation, project-prep, contract, consistency]
metadata:
  hermes:
    tags: [documentation, project-prep, contract, consistency]
    category: software-development
---

# 项目全套技术文档生成（doc suite authoring）

## 触发条件
- 用户要求"生成相应的项目开发相关技术文档"（需求/架构/API/测试/概要/数据库/详细设计等）
- 用户给出投标书/甲方需求文档，要求工程化改写为可开发文档
- 多 Agent 开工前需要完整文档体系（配合 `multi-agent-protocol` / `project-constitution-authoring`）

## 文档体系结构（已验证有效的 8 件套）
按依赖顺序生成，前一文档是后一文档的权威源：

1. `docs/REQUIREMENTS.md` — 需求权威源：FR 编号化（FR-M-N）、验收指标可执行化、分期表
2. `docs/01-architecture.md` — 分层架构、核心业务流程、技术选型理由、风险对策
3. `docs/02-api-design.md` — 全局规范（统一响应/错误码/RBAC）+ 模块接口 + 契约冻结规则
4. `docs/03-test-cases.md` — 用例编号 TC-模块-分类-序号（F/N/E/A/S/P）+ 答辩证据目录
5. `docs/04-overview-design.md` — 模块划分/DRI/ADR/状态机/时序/事件类型全集
6. `docs/05-database-design.md` — 冻结 DDL、向量集合、Redis key、PII 加密
7. `docs/06-detail-design.md` — 冻结 Schema（数据类）、核心算法、关键实现要点
8. `DEVELOPMENT_GUIDE.md` — 多 Agent 协作（固定编制/模型分层/G 门禁/里程碑）

每份文档头部写：版本/状态/维护者/前置文档；正文写"文档优先级"（权威源 > 冻结契约 > 任务书 > 聊天）。

## 工作流程

### 1. 侦察输入
读用户提供的参考文档/口述，识别：业务需求全集、技术栈、验收指标、分期。用户需求逐条保留，不擅自砍。

### 2. 投标书指标去水（关键工程化步骤）
甲方/参考文档常含**无法验收的指标**：`准确率≥99%`、`杜绝幻觉`、`2000并发/99.9%可用率`、`十亿级向量`。
→ 改写为**测试集口径 + 统计指标 + 可执行验收**（如"自建 100 份样本字段抽取 F1≥0.85"）。
→ 性能/规模指标降为 MVP 口径并在文档中注明"该边界即为专业判断"（答辩加分）。

### 3. 按依赖顺序生成
先 REQUIREMENTS（FR 编号是全局锚点），再架构/API/数据库/测试/设计/开发指南。API 路径、表名、Schema 字段必须逐字引用自上游文档。

### 4. 交叉一致性审计（必做，别等用户查）
生成完立刻按 `references/consistency-audit-checklist.md` 自查一遍。用户/reviewer 会做同样的交叉分析，主动自查可省一轮返工。

## 用户偏好（已验证）
- **不砍需求**：用户明确"不要以初学者角度看待项目要求"→ 保留全部业务需求，用**工程分期（一期/二期）**代替砍需求；技术栈也同理（如 Dify 一期直连兜底、二期正式接入 = 架构要求保留 + 落地节奏分期）。
- **答辩含金量**：文档必须内建"量化证据"——自建评测集、对比实验（规则 vs 向量 vs 融合）、合成演示数据（禁真实 PII）。
- **修复按严重度排序**：交叉分析问题按 硬伤→缺口→决策→瑕疵 顺序处理，每项先给明确裁决（保留/补/改/删）再动手。
- **契约一致高于一切**：FR 编号、Schema、API 路径、表名、结局标签等跨文档必须逐字一致。

## Pitfalls
1. **编号悬空**：文档引用的编号（FR-x.y、TC-x、章节号）必须存在且连续；改编号时全局 grep 检查引用。
2. **表有 API 缺**：设计了表/事件但没有驱动接口 → 契约无法产生（如 offer_orders 表无 Offer API，结局标签状态机没有入口）。
3. **定义冲突**：同一概念在不同文档值集不一致（结局标签 3 值 vs 4 值）→ 以需求权威源为准统一。
4. **概念混用**：示例字段把事件类型写进结局标签字段（outcome_label: "offer_sent"）。
5. **口径漂移**：同一技术在不同文档表述不一（Dify"一期"vs"二期"）→ 以 ADR 为唯一口径，需求技术栈表同步注"口径（与 ADR-x 一致）"。
6. **隐藏工作量**：评测集构建/合成数据不排期 → 里程碑要显式排（如 MS1.5），指定 DRI、先于被测模块完成。
7. **架构文档滞后于需求权威源**：需求改版后必须回扫 01-architecture / 开发指南 / 测试用例，grep 旧值确认 0 残留。

## 支持文件
- `references/consistency-audit-checklist.md` — 跨文档一致性审计清单（生成后自查 + 评审他人文档用）
