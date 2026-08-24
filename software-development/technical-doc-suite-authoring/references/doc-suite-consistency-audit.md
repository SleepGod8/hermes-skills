# 跨文档契约一致性审查 · P0 深水区案例库（AI 人才平台六轮审查沉淀）

来源：AI 数字化人才智能平台 8 份文档生成 + 六轮交叉审查的真实修复记录。作为生成同类文档套件时的审查模板与严重度参考。

## 审查轮次演进

| 轮次 | 发现 | 严重度 |
|---|---|---|
| 1 | 结局标签 3/4 值冲突、offer 有表无 API、候选人账号缺失、前端范围模糊、示例值概念混用、章节跳号、Dify 口径 | A-E（硬伤→小瑕疵） |
| 2 | 架构文档滞后需求、FR 编号悬空、churned 无驱动入口、TC 编号悬空 | 半开/小瑕疵 |
| 3 | Offer FR 引用错、前端未排里程碑、证据目录缺失、拼写 | 毛毛刺 |
| 4 | MS4.5 未同步、前端 DRI 未定、页面映射缺 Offer 页 | 观感级 |
| 5 | 令牌 5 名并存、Dify 定位不一致、offer_accepted 合并 onboarded、事件写入无校验、API 契约未冻结 | **P0 深水区** |
| 6 | 向量维度未冻结、user_role 信任请求、PII 密钥无托管、E2E 无人值守矛盾、Excel 格式范围、方差统计口径 | P1 风险 |

## P0 深水区修复模式（第 5 轮核心）

### 1. 令牌方案统一为两阶段
- 问题：initial_token / candidate_token / access_token / Bearer / 一次性 / 可重复 六种表述并存
- 修复：**两阶段令牌**
  - 阶段 A（发放）：HR 调 `interview-token` → 一次性 `exchange_token`（绑定 candidate_id+interview_id，TTL 24h，Redis 存，即用即删防重放）
  - 阶段 B（兑换）：候选人调 `candidate-login` → 短期 `candidate_jwt`（Bearer，TTL=业务时限，scope 绑定，业务完成后进 Redis 黑名单失效）
- 规则：面试期间可多次读题/作答；submit 后失效；Offer 操作由 HR 代操作不开放候选人自助

### 2. 业务状态不合并
- 问题：offer_accepted → onboarded 直接合并（接受 Offer ≠ 实际入职）
- 修复：`offer_sent → offer_accepted → accepted_offer → onboarded → churned`，中间允许放弃（→ withdrawn）
- 新增 `POST /candidates/{id}/onboard` 入职确认接口（HR 实际报到后调）
- 幂等表：状态不匹配 40000；同状态重复幂等 200；权限一律 HR/管理员代操作留审计

### 3. 事件写入枚举 + 转换校验
- 问题：POST /events 的 event_type 是自由字符串
- 修复：13 值强制枚举 + 状态转换表（当前状态→允许事件→下一状态，10 行）作为单一权威源（core/events.py）；非法枚举/非法转换 40000 不落库

### 4. API 契约冻结细节
- 每个端点定死同步/异步：jds/generate 定同步（单次 LLM ≤30s），解析/匹配/报告走异步 202 + task
- 统一响应包装约定：示例只展示 data，外层 code/message/trace_id 省略（写进 §1.2 全局规范）
- 字段名与 DB 一致：resume 接口 `status` → `parse_status`
- 枚举拼写全库统一：`generating` → `generating_questions`（API/状态机/测试三处）
- 每张 DB 表有管理 API：positions 补 POST/GET/PUT

## P1 风险处置

| 项 | 处置 |
|---|---|
| 向量维度 | 冻结 bge-m3/1024 维，换模型必须 4 步迁移（配置/重建集合/更新文档/Eos 验收） |
| qa 权限 | 移除 user_role 请求参数，角色从 JWT 解析 |
| PII 密钥 | 环境变量托管 + 双 key 轮换（ACTIVE/PREV）+ 备份分离 |
| E2E 无人值守 | 候选人答题用测试代理（预置答案），复试用固定表单，人工节点可被代理代替 |
| Excel 格式 | 一期不含 Excel（表格需结构化解析），PDF/Word/TXT/Markdown/图片 |
| 方差定义 | 统一"极差（max-min）≤1.0 档"，非统计方差 |
| 评测集未建 | 标"规划交付物，MS1.5 落地，不得虚构" |

## 审查修复协议（处理 review 报告）

1. 按严重度逐项修：P0 → P1 → 观感级；建 todo 跟踪
2. 每项修完用 search_files 全库验证零残留（搜旧值：initial_token / 4.4.x / onbaorded）
3. 引用反向同步：改编号/名称必须搜全部引用处；新增 API → 同步测试 + 页面映射 + 证据目录
4. 统一口径写"为什么"，并在需求表/ADR/架构多处互引
5. 修复报告用表格：问题编号 + 改动文件 + 处理 + 验证结果
6. 裁决类问题给推荐 + 业务理由（如 churned 保留：归因分析需追踪入职后流失）

## 坑清单

- markdown 表格 patch 会吃掉相邻 `###` 标题行（真实发生：3.4 标题被覆盖）
- 插入小节后编号跳号要全库重查
- 改权威源必须逐下游文档核对，不能只改一处
