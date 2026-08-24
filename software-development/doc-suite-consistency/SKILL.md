---
name: doc-suite-consistency
description: "Use when 生成/维护多文档项目套件或做跨文档一致性交叉审查。"
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [doc-consistency, requirements, architecture, api-design, cross-review, contract]
    category: software-development
    related_skills: [project-constitution-authoring, agent-task-book-authoring, project-requirements-analysis]
---

# 多文档套件一致性（Doc Suite Consistency）

大型项目常生成整套技术文档：`REQUIREMENTS` + `01-architecture` + `02-api-design` + `03-test-cases` + `04-overview-design` + `05-database-design` + `06-detail-design` + `DEVELOPMENT_GUIDE`。文档之间契约不一致是最大风险——实战验证（AI 人才平台项目，九轮交叉审查磨出本方法）。

## 触发条件

- 用户要求生成整套项目技术文档（需求/架构/API/测试/概要/数据库/详细设计）。
- 用户要求"交叉分析/排查/审查"文档间一致性。
- 项目文档更新后需要全链同步（改枚举/状态机/角色/schema）。
- 开发前要冻结契约，避免开发位照旧版实现踩坑。

## 核心原则

1. **单一权威源**：每类契约只在一个文档定义，其余引用它。
   - REQUIREMENTS = 最高需求权威源（FR 编号）
   - 状态转换表 / 错误码表 / 令牌方案 / Schema = 各选一个文档冻结，禁止多处各自实现
2. **改动全链同步**：改枚举、状态机、角色、schema 时，需求/架构/API/DB/测试/页面映射全部同步；任一滞后 = 开发位踩坑。
3. **交叉审查是必经流程**：文档生成后做多轮全文交叉审查，按严重度排序问题清单，逐项修复 + 全局 grep 验证零残留。
4. **双码约定**：业务 code 与 HTTP 状态码成对定义（如 42200↔422、40000↔400），前端以 code 为准，禁止裸 422/40000 无映射写法。
5. **事务一致性**：事件写入 + 状态更新必须在同一 DB 事务 + 幂等键（DB 唯一索引兜底），禁止"事件已写、状态未更"中间态。

## 高频冲突模式（每轮必查清单）

| # | 模式 | 示例 | 修复要点 |
|---|---|---|---|
| 1 | 结局/状态标签定义冲突 | 上游 4 种结局 vs 下游 3 种 | 以权威需求源为准，全链补齐 |
| 2 | 状态机转换无 API 驱动 | 转换表允许 accepted→withdrawn 但无接口 | 补接口或明确内部触发路径 |
| 3 | FR 编号悬空 | API 引用不存在的 FR-3.9 | 补 FR 或改引用，且改完 grep 验证 |
| 4 | 错误码双码不统一 | 局部写 422/40000，全局要求 code=42200 | 建立 §1.3 双码映射表，测试同步 |
| 5 | 幂等键契约缺口 | DB 必填但 Schema/API 示例/测试都没有 | 公共 IdempotentRequest + 全局规则 + 缺失/重复/复用用例 |
| 6 | 租户隔离缺失 | 多企业系统表缺 company_id | 表 + 向量 metadata + 检索预过滤全链加 |
| 7 | 角色枚举未同步权威源 | API/DB 加 employee，REQUIREMENTS/架构仍 4 角色 | 需求用户表 + 架构 RBAC + API RBAC + DB role + 测试同步 |
| 8 | 令牌/授权概念混用 | 一次性 token vs 会话 JWT 未区分 | 两阶段方案：exchange_token（一次性）+ 短期 JWT（可复用），全文档统一命名 |
| 9 | 测试编号引用失效 | 用例拆分后旧引用未更新 | 文档引用与测试文档编号同步，grep 旧编号 |
| 10 | 前端映射遗漏 | 页面↔接口表缺 onboard/churn 等新接口 | 新接口必入映射表 + 里程碑 + DRI |
| 11 | 里程碑未排工作量 | 评测集构建/前端页面集没有显式排期 | MS1.5 等子里程碑显式列出，含 DRI |
| 12 | 版本与口径 | 一期不部署 Dify 但架构文档仍列部署项 | 部署/性能/风险表全链统一"一期路径 vs 二期路径" |

## 工作流

### 阶段 A：生成文档套件
1. 先定权威源层级（需求 → 架构 → API → DB → 测试 → 详细设计 → 开发指南）。
2. 生成时用统一编号体系：FR-x.y、TC-<模块>-<分类>-<序号>、事件枚举、角色枚举。
3. 每份文档头部标注"前置文档 + 契约属性（冻结/参考）"。
4. 冻结接口/DDL 标"开发位不得擅改；变更走负责人批准"。

### 阶段 B：交叉审查（可多轮）
1. 逐份文档通读，按严重度排序问题（硬伤 > 缺口 > 决策 > 小瑕疵）。
2. 重点核对：FR 引用、状态机 vs API、错误码映射、幂等键、租户隔离、角色枚举、令牌方案、测试编号、前端映射、里程碑排期、口径统一。
3. 修复遵循"权威源先行，下游跟随"，每轮修复后全局 grep 验证零残留。
4. 遗留"可提可不提"的观感级问题也建议顺手统一，避免噪音累积。

### 阶段 C：冻结
- 全部一致后升版本号（v1.0 → v1.1）+ 变更记录。
- 声明可开工条件：状态机闭环、令牌两阶段、角色全枚举、权限双端校验、幂等防重、租户隔离、错误码双码。

## 验证命令模式

```bash
# 全局搜残留旧引用（改完必跑）
rg "旧编号|旧状态名|旧枚举|旧角色|拼写错误" <project_dir>
# 确认某字段跨文档一致
rg "churned|employee|idempotency_key|company_id" <project_dir>
```

## 支持文件

- `references/doc-suite-consistency-checklist.md` — 完整跨文档审查清单（九轮实战沉淀，含状态机/错误码/幂等/租户/角色/令牌/里程碑检查项）。
