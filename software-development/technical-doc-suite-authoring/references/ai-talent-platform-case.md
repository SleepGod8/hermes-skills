# AI 人才平台案例：7 件套结构 + 交叉分析 A-F 修复

本文件记录 2026-08 会话的完整案例，作为技术文档套件生成的模板参考，同时保存项目背景（内存熔断未能存入 memory）。

## 项目背景（答辩/面试项目）

- 项目名：AI 数字化人才智能平台（AI 人才平台）
- 目录：`E:\Hermes workspace\ai-talent-platform\`
- 面向：招人公司/人力公司/软件外包公司（ToB）
- 定位：个人全栈项目，用于答辩/面试介绍，要求有含金量
- 技术栈：FastAPI + SQLAlchemy + LangChain/LangGraph + MySQL + Milvus + Redis + Vue3（一期）；Dify/PgSQL/Vanna/语音面试二期
- 一期范围：M1-M5 全模块 MVP + Vue3 最小页面集（8-12 周单人）

## 5 大功能模块

| 模块 | 功能 | 核心难点 |
|---|---|---|
| M1 JD 生成 | 模糊需求→结构化 JD（Schema 契约） | JD Schema 是 M2 地基 |
| M2 简历匹配 | 解析+硬过滤+语义匹配+可解释报告 | 三层融合（规则+向量+LLM） |
| M3 AI 初面 | 问题生成/异步答题/Rubric 评分 | 评分一致性校准 |
| M4 画像沉淀 | 复试采集/画像/事件流 | 事件流 append-only + 结局标签 |
| M5 入职问答 | 知识库 RAG/溯源/权限 | 检索质量 + 权限隔离 |

## 关键契约决策（已冻结）

- 结局标签 4 种：onboarded / rejected / withdrawn / churned（churned 必须保留，归因分析需要）
- 事件类型全集：applied → resume_parsed → matched → ai_interview_started → ai_interview_completed → screening_reviewed → human_interview → offer_sent → offer_accepted → onboarded/rejected/withdrawn/churned
- Offer 状态机：draft → sent → accepted | declined（accept→onboarded，decline→withdrawn）
- 候选人免登录：一次性答题令牌（Bearer，Redis 存，绑定 interview_id，防重放）
- 匹配评分：0.4*语义 + 0.6*LLM 交叉，四维可解释（技能/经验/教育/软素质）
- 评分一致性：Rubric + 低温采样 + 5 次取中位，方差 ≤1.0 档
- Dify 口径：一期 LLM 直连适配层跑通，二期接 Dify（接口预留，与 ADR-2 一致）

## 文档 7 件套（本项目实际产物）

```
E:\Hermes workspace\ai-talent-platform\
├── DEVELOPMENT_GUIDE.md        # 多agent开发指南（固定编制/门禁/里程碑）
└── docs\
    ├── REQUIREMENTS.md         # 需求权威源（FR 编号）
    ├── 01-architecture.md      # 技术架构
    ├── 02-api-design.md        # API 契约（冻结）
    ├── 03-test-cases.md        # 测试用例（60+ 用例）
    ├── 04-overview-design.md   # 概要设计（ADR-1~10）
    ├── 05-database-design.md   # 数据库（MySQL 18 表 + Milvus 5 集合）
    └── 06-detail-design.md     # 详细设计（冻结 Schema + 算法）
```

## 交叉分析 A-F 问题（用户打回的真实硬伤 → 修复模板）

| # | 问题 | 根因 | 修复 |
|---|---|---|---|
| A | 结局标签定义冲突：需求 4 种（含 churned），设计只有 3 种 | 枚举多文档未同步 | 裁定 churned 保留，三处文档统一 |
| B | offer 有表无 API | 表设计先行，接口遗漏 | 补 §6.2 Offer API（5 接口）+ 测试用例 |
| C | 候选人账号体系缺失 | 身份流程未闭环 | 补 §2.3 候选人接口 + 答题令牌设计 |
| D | 前端范围模糊 | 决策悬置 | 裁定一期 Vue3 最小页面集，写入 ADR-10 |
| E | 小瑕疵：示例值概念混用/章节跳号/Dify 口径 | 生成后未自查 | 统一示例、grep 修编号、口径对齐 ADR |
| F | 评测集构建未排期（隐藏工作量） | 里程碑遗漏数据准备 | MS1.5 显式排期，Eos 主责 |

## 答辩/面试讲法（本项目）

- 主线：一条候选人从投递到入职的全流程故事 + 两个深点（匹配可解释性、评分一致性校准）
- 证据：自建评测集（100 简历/50 匹配标注/50 问答/20 面试抽样）+ 对比实验 + 方差报告
- 术语口径：企业级架构按 MVP 节奏交付，Dify 二期接入，性能指标按单机 50 用户验证
