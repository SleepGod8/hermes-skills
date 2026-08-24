# 跨文档一致性审查清单（九轮实战沉淀）

来源：AI 数字化人才智能平台项目，8 份文档 × 9 轮交叉审查。每轮问题按严重度排序（硬伤 > 缺口 > 决策 > 小瑕疵 > 观感），修复后全局 grep 验证零残留。

## 1. 权威源层级（先定这个再动手）

1. `REQUIREMENTS.md` — 最高需求权威源，FR 编号（FR-x.y）
2. `01-architecture.md` — 架构/流程/部署
3. `02-api-design.md` — 接口契约、错误码、RBAC（**接口契约冻结处**）
4. `05-database-design.md` — DDL（**表结构冻结处**）
5. `06-detail-design.md` — Schema、算法、令牌设计
6. `04-overview-design.md` — 模块/状态机/ADR
7. `03-test-cases.md` — 测试用例
8. `DEVELOPMENT_GUIDE.md` — 协作协议、里程碑

## 2. 每轮必查的 12 类冲突

### 2.1 结局/状态标签定义冲突
- 结局标签（onboarded/rejected/withdrawn/churned）必须全文档一致，包括事件流全集、状态机、DB 字段注释。
- 典型案例：REQUIREMENTS 定义 4 种结局含 churned，下游 overview/database 只有 3 种。裁决：churned 保留（归因分析要"减少频繁人力流动"），全链补齐。

### 2.2 状态机转换无 API 驱动
- 转换表允许的每条转换必须有驱动入口（API 或明确内部触发路径）。
- 典型：accepted_offer→withdrawn 只有转换表没有接口 → 补 `PUT /offers/{id}/withdraw`；早期阶段退出 → 补 `POST /candidates/{id}/withdraw` 通用入口。
- 检查：状态机每个箭头 → 找到对应接口；无接口的转换必须显式写"内部服务触发"。

### 2.3 FR 编号悬空
- API/测试引用的 FR 编号必须真实存在于 REQUIREMENTS。
- 典型：API §2.3 引用 FR-3.9，但模块 3 只有 FR-3.1~3.8 → 补 FR-3.9 或改引用。
- 修复后 grep 该编号确认三处对齐（需求 + API 引用 + 一期范围表）。

### 2.4 错误码双码不统一
- 全局定义业务 code ↔ HTTP 状态码映射表（0↔200、40000↔400、40100↔401、40300↔403、40400↔404、42200↔422、42900↔429、50000↔500、50400↔504）。
- 前端以 code 为准，HTTP 只作传输语义。
- 边界：Pydantic/枚举非法 → HTTP 422 + code=42200；业务状态机非法 → HTTP 400 + code=40000。
- 禁止裸 422/40000 无映射写法；测试用例也要写双码。

### 2.5 幂等键契约缺口
- 所有状态变更接口（offer 各操作、onboard、churn、withdraw、事件写入）必须携带 idempotency_key。
- 公共 Schema：`IdempotentRequest { idempotency_key: str }`；事件表加 `(candidate_id, idempotency_key)` 唯一索引。
- 规则表：缺失 → 40000；重复（同 key 同操作）→ 200 幂等返回；跨操作复用 → 40000；TTL 1d。
- 测试必须覆盖：缺失/重复/复用 三用例。

### 2.6 租户隔离缺失
- 多企业系统：所有租户数据表（knowledge_docs/kb_chunks 等）+ 向量 metadata + 检索预过滤必须含 company_id。
- company_id 取自 JWT 所属企业，不信任请求体。
- 检索条件 = company_id + permission_scope 预过滤（Milvus 过滤表达式 + BM25 过滤）。

### 2.7 角色枚举未同步权威源
- 新增角色（如 employee）必须同步：REQUIREMENTS 用户表 + 架构 RBAC + API RBAC 表 + DB role 字段 + permission_scope 枚举 + 测试。
- 角色转换规则（如 candidate→employee 在 onboard 时）要在 API RBAC 注明。

### 2.8 令牌/授权概念混用
- 统一两阶段：一次性 `exchange_token`（HR 发放，绑定 candidate+interview，即用即删防重放）+ 短期 `candidate_jwt`（Bearer 会话，面试提交后失效）。
- 禁止出现多个名字（initial_token/candidate_token/access_token/Bearer 混用）；全文档统一命名。
- ADR 摘要也要同步（否则架构决策层残留旧模型）。

### 2.9 测试编号引用失效
- API 文档引用的 TC 编号与测试文档实际编号必须同步；用例拆分（F-05 → F-05a/b/c）后旧引用全清。
- grep 旧编号 `TC-M4-F-05/06/07/10` 之类复合引用。

### 2.10 前端映射遗漏
- 新接口必须进页面↔接口映射表（§9 类）；遗漏导致页面无法覆盖完整流程。
- 同时检查：里程碑是否排了前端页面集（MS4.5）、DRI 兜底链（Aphrodite→Eos→Athena）是否定案。

### 2.11 里程碑未排工作量
- 隐藏工作量必须显式排期：评测集构建（100 简历/50 匹配/50 问答/20 面试抽样）、合成演示数据、前端页面集。
- 加 MS1.5 类里程碑 + 明确 DRI（Eos 主责、Ares 辅助），避免开发位"没评测集不自测"。

### 2.12 版本与口径
- 一期 vs 二期口径全链统一：技术栈表、部署架构、性能表、风险表、ADR 必须一致（如"一期直连 LLM，Dify 二期接入"）。
- 需求文档技术栈表要直接写明口径，防止答辩被追问穿帮。

## 3. 业务语义类硬伤（特别注意）

### 3.1 事件/结局语义
- offer_accepted（接受 Offer）≠ onboarded（实际入职）——中间允许放弃（→withdrawn）。
- Offer 状态机显式分支：`draft → sent → accepted → withdrawn` 或 `sent → declined`。
- 事件写入必须枚举校验 + 状态转换表 + 事务一致性 + 幂等键。

### 3.2 内部服务令牌
- 内部接口（POST /events）用 service token：来源环境变量、格式 `svc_` 前缀 Bearer、与用户 JWT 区分（认证中间件按前缀分流）、轮换（24h 宽限期）、审计（actor_type=service）。

### 3.3 问答会话归属
- qa:thread 存储 {user_id, company_id, permission_scope}，查询/续聊校验归属一致否则 40300（防跨用户读取）。

## 4. 修复流程（每轮）

1. 逐份文档通读，产出按严重度排序的问题清单（表格：编号/位置/问题/建议修复/是否阻塞）。
2. 权威源先行修复（先改 REQUIREMENTS），下游跟随。
3. 每项修复用 patch 精确替换；同文件多处修改用 V4A patch 合并。
4. 修复后全局 grep 验证：`rg "旧编号|旧枚举|旧角色|拼写" <dir>` 应为 0。
5. 一致性验证：`rg "关键字段" <dir>` 确认所有文档出现且语义一致。
6. 观感级问题（拼写、编号顺序、标题残留）顺手清理，避免累积。
