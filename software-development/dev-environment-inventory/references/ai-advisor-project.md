# AI 投顾 Agent 项目（AI投资助手）· 盘点实例与开发基线

> 2026-08-10 研究分析会话产出（只分析未开发）。用户 @Athena 要求读取需求文档、列出未装依赖、分析架构/数据库/阶段/团队分工、多 agent 分工。
> 多 agent 开发本项目时，开发流程协议加载 `multi-agent-protocol`，本文件提供项目事实来源。

## 需求文档位置（本机缓存）

- 42 篇全部缓存于 `C:\Users\80704\AppData\Local\hermes\workspace\feishu_import\markdown\`
- 核心文档：`0金融投顾类AI产品思考`、`1产品立项书撰写思路`、`4产品功能范围与边界说明`、`5MVP产品方案`、`7模型技术架构方案`、`8风险控制与合规留痕方案`、`9项目排期与资源预算`、`AI投顾Agent开发方案`（工程落地版，含 SQL 与接口）、`6目标用户与核心场景分析`
- ⚠️ `README.md` 与 `ARCHITECTURE.md` 是 **RIC-Train（跨境电商 AI 工作台）** 的文档，不是本项目文档，别混淆。

## MVP 定位与范围

- 定位：AI 金融信息解读与投资分析辅助工具（对外称“AI投资助手”，不称“投顾/荐股”）
- 周期：12–16 周；上线：内部测试 → 白名单灰度 → 小流量
- MVP 功能：AI 问答入口、市场解读、个股通用分析、财报解读、公告解读、投资知识问答、高风险识别(R0–R5)、输出合规审核、事实校验、RAG 知识库、金融工具调用(P0×5)、日志留痕、审计后台(简版)、用户反馈、灰度控制
- MVP 不做：AI荐股、明确买卖建议、自动下单/调仓、持仓诊断、收益预测、短线信号、跟投带单

## 本机环境盘点（2026-08-10 实测）

✅ 已具备：Docker 29.6.2（容器：milvus-standalone 19530 / my-redis 6379 / milvus-minio 9000 / neo4j / nginx / dify 全家桶）；**MySQL 9.7.0 本机服务 3306（非容器，socket banner 确认）**；Node v24.18.0+npm 11.16.0；Python 3.13.5（系统+conda base E:\conda，**无 fastapi**）；Ollama 仅 bge-m3（embedding）；pip 已有 SQLAlchemy 2.0.39 / pymilvus 3.0.1 / pandas / httpx / cryptography；API key 已有 DeepSeek / DashScope / ZhipuGLM / Agnes-AI

❌ 未装（开发前需装）：fastapi+uvicorn、pymysql、langchain/langchain-community/langgraph、openai、redis、PyJWT、akshare、jieba、（可选 dashscope/celery/pydantic-settings）；前端全新工程（vite+react+antd+axios+zustand）；金融数据源未配置；本地对话大模型缺失（建议走 DeepSeek API）

⚠️ 本机无 wolin conda 环境、无 D:\PythonProject（那是另一台机的记忆）；建议 `conda create -n ai_advisor python=3.13` 隔离

## 数据库设计基线（文档给出 SQL，MySQL 语法）

留痕/日志表：`ai_query_log`、`ai_risk_log`、`ai_model_call_log`、`ai_final_answer_log`、`ai_tool_call_log`、`ai_rag_log`、`ai_fact_check_log`、`ai_compliance_log`、`ai_feedback_log`、`ai_audit_operation_log`
需自行设计：`users/user_permissions`（user_id 存 hash 脱敏）、`sessions`、`ai_prompt_templates`、`ai_high_risk_samples`、`ai_gray_config`、`ai_monitor_metrics`
选型：MySQL(业务) + Redis(缓存/会话) + Milvus(向量RAG) + MinIO(对象存储) — 本机全就绪

## 阶段（12–16 周 / 6 阶段）

阶段0 立项方案(1–2周,M0) → 阶段1 基础架构(3–4周,M1 网关/会话/模型/日志) → 阶段2 数据工具+RAG(5–8周,M2) → 阶段3 Agent场景+前端(7–11周,M3) → 阶段4 风控合规+审计后台(9–13周,M4) → 阶段5 测试红队灰度上线(12–16周,M5–M7)

## 多 Agent 分工映射（按 multi-agent-protocol）

- Agent1 项目负责人=PM+集成发布+灰度；Agent2 架构=ARCH/接口契约/DDL；Agent3 FEAT-01 网关+会话+模型+Prompt管理；Agent4 FEAT-02 数据接入(akshare)+P0工具+RAG；Agent5 FEAT-03 意图/实体/风险识别+Agent调度+合规重写+前端；Agent6 TEST 功能/接口/红队8类样本+合规评审+安全脱敏；Agent7 候补=投研评测/运维脚本，仅 Agent1 分派
- 合并顺序：契约→数据模型→FEAT-01/02/03→测试→审查修复→发布；`ai_*_log` DDL 仅归 Agent2 写
- 质量门禁：高风险误放 0、风险提示缺失率 0、留痕完整、红队样本全通过
- 模型熔断：DeepSeek API 超时 90s，连续失败降级兜底话术（架构文档要求）
