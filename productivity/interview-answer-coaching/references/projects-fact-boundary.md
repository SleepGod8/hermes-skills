# 三个项目的取证地图与事实边界

主人的简历三个项目 + 对应文档位置。答任何项目题先来这里定位，再动笔。

---

## 1. AI 数字化人才智能平台（2025.10–2026.9）

**文档**：`E:\Hermes workspace\面试\ai-talent-platform\docs\`
`REQUIREMENTS.md`（需求权威源 v1.2）/ `02-api-design.md` / `03-test-cases.md` / `05-database-design.md` / `06-detail-design.md`

**一句话**：JD 生成 → 简历匹配 → AI 初面 → 人工复试 → Offer/入职问答 → 候选人画像与事件流。
技术：FastAPI + SQLAlchemy + LangChain/LangGraph + Milvus + Redis + MySQL + Vue3 + ECharts + SSE。

**他主责**：JD 意图拆解 + 岗位能力模型 RAG + Schema 校验；三层融合匹配；异步文字初面 + Rubric 低温采样；事件流幂等。

**可直接引用的机制**（可信度最高的答题素材）：

| 机制 | 出处 | 值/口径 |
|---|---|---|
| JD Schema 契约 | 06 §3.1 | `JDSchema` 字段级；权重和=1.0，校验失败归一化 |
| LLM 适配层 | 06 §6 `core/llm.py` | `complete(prompt, schema, temperature=0.2, max_retries=3)`，失败重试→`LLMValidationError`→blocked |
| 评分一致性 | 06 §4.3 / 03 TC-M3-A-01 | 低温 0.2、同答案采样 5 次、取中位、记 max-min 极差，**极差 >1.0 档标 low_confidence 转人工** |
| 合规扫描双层 | REQ §3.7.5 / M7 | 规则词库 + LLM 语义审查，**两层取并集，任一层命中即报**；误报率目标 ≤15% |
| 匹配三层融合 | 06 §4.1 | 规则硬筛（任一 blocked 上限压 50）→ 向量语义 → LLM 四维交叉（temp 0.2）；`total=0.4*semantic+0.6*cross` |
| 幂等矩阵 | REQ §5.1 / 03 TC-INF | `idempotency_requests` 永久表；客户端 UUID4、worker UUID5 确定性键；processing 租约 5 分钟 |
| 事件流 | REQ §3.4.5 | append-only；4 种结局标签 onboarded/rejected/withdrawn/churned |
| M1 验收 | REQ §3.1.6 | Schema 通过率 ≥99%、核心字段非空 100%、**人工可读性 10 份 JD / 5 人 ≥4/5** |

**边界**：M1–M9 全是设计文档，评测集与证据目录明确写着"规划交付物，尚未创建"。任何准确率都不能说成实测。Dify、Vanna.ai、PgSQL、实时语音=二期。

---

## 2. AI 就业教练智能平台（2024.6–2025.10）

**文档**：`E:\Hermes workspace\面试\job-coach-platform\docs\`

**一句话**：简历优化 → 面试陪练 → 薪资谈判 → 入职引导，四类教练 Agent 状态机 + 多知识库 RAG + 顾问案件联动。

**可引用**：
- 长任务异步化 + SSE 进度；WebSocket 承载对话流式（01-architecture §）
- `core/llm.py` 统一适配层：多 provider 路由 + 重试 + 缓存 + fallback DeepSeek（主力层超时/401/429/stale → 降级）
- Redis：会话缓存、令牌桶限流 `rate:{user_id}:{endpoint}`（1min）、任务队列、LangGraph checkpoint
- 连接池：SQLAlchemy pool + Redis pool（01-architecture 性能章）
- 图：`resume_optimization_graph` / `interview_coaching_graph` / `onboarding_graph`，validate 失败重试 ≤3
- 性能基线（03 TC-P-01..08）：普通接口 p95 ≤1s、向量检索 ≤500ms、简历解析 ≤30s、优化报告 ≤60s、面试报告 ≤90s、问答 p95 ≤5s
- 评分一致性：同 M3，5 次采样极差 ≤1.0 档

**边界**：性能基线是 P1 验收目标，不是压测实测结果。

---

## 3. 智能财富管家（2023.7–2024.6）

**代码**：`E:\项目\smart-wealth`（三个项目里**唯一有真实代码**的，可以大胆引实现细节）
**他主责**：风控规则引擎、风险 Agent、NL2API、权限校验、二次确认、工单联动、业务操作线。

**可引用的真实代码事实**：

| 事实 | 位置 |
|---|---|
| `emit()` 统一发布，禁手写 `redis.publish`；未登记 event_type/source_agent 直接抛 ValueError | `app/tool/bus.py:51-96` |
| Redis 失败 → 降级 `_memory_emit`，只 warn「事件发布降级(内存, 跨节点订阅者将丢失)」，跨节点消息静默丢 | `bus.py:73-87` |
| `emit()` 发布成功后 `return False`，**publish 的返回订阅者数量被丢弃**——调用方无法用返回值判断送达 | `bus.py:73-77` |
| 监听线程 `_listen()` 异常只 warn「Redis pubsub listener 退出: %s」**不重连**，之后该类型事件全丢 | `bus.py:157-173` |
| 内存订阅回调异常被吞成 warning，不落任何消费记录 | `bus.py:120-128` |
| 日志格式 | `app/utils/logger.py:67` → `%(asctime)s [%(levelname)s] trace=%(trace_id)s %(name)s: %(message)s` |
| 真实日志样本（项目自带 logs/） | `2026-08-11 20:24:10,819 [WARNING] trace=t-xxx app.tool.bus: Redis pubsub listener 退出: I/O operation on closed file.` |

**边界**：统一 Agent 骨架、GraphRAG、四层记忆、事件总线属**架构组维护的共享骨架**，他只参与联调。回答必须说清"骨架是团队范围，我在风控/操作线联调时踩过这些坑"，否则算职责漂移。事件总线当前语义是至少一次、依赖幂等消费，不能说成 exactly-once。

---

## 通用红线

1. 设计文档 ≠ 已上线。没数字就说"示例参数，需实测标定"。
2. 团队能力（骨架/图谱/记忆）不能说成个人独立完成。
3. 不编模型版本、参数、阈值、客户名。
4. 被追问"实际跑下来多少"时：诚实说没有生产数据，给"我会怎么定阈值"的方法（见 answer-bank 第 2 题）。
