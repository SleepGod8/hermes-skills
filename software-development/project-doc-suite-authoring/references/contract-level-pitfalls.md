# 契约级交叉审查补充项（P0 类，后期审查高频）

来源：AI 招聘平台文档体系 10 轮交叉分析后半段（2026-08，契约级问题）。

## 1. 错误码双码映射只有一处

- 全局定义 HTTP 状态码 + business code 映射表（422↔42200 / 400↔40000），其他文档只引用不重写
- 典型：06-detail 写"非法→422/40000"、02-api 写"非法值→40000"，三处三个值
- 边界：Pydantic/Schema 校验失败（含枚举非法）= HTTP 422 + code=42200；业务状态机失败 = HTTP 400 + code=40000
- 验证：grep `422/40000`、`非法值 → 40000`、`非法转换 → 40000\b`

## 2. 幂等键四层缺失

- 典型：DB 字段 NOT NULL 但请求 Schema/API 示例/测试都没有；"同 key 重复 vs 复用"无判定依据
- 四层齐：① 请求 Schema（必填）② API 规则（缺失/重复/复用返回表 + **数据指纹** `{operation, resource_type, resource_id, request_hash}`：四要素全等=同操作重复→200 幂等；任一不同=跨操作/资源复用→40000）③ DB 唯一索引 `(candidate_id, idempotency_key)` 兜底 ④ 测试（缺失/重复/复用三用例）
- 事务一致性：状态变更 = 业务状态 + 候选人状态 + 事件追加必须同一 DB 事务，任一步失败整体回滚，禁止中间态

## 3. 租户隔离缺 company_id

- 多企业系统：知识库/候选人无租户字段会串读；company_id 不信任请求体
- 五处齐：表结构（文档/分块冗余存，免 JOIN）→ Milvus metadata → 检索预过滤（company_id + permission_scope）→ 上传/查询服务端校验（取 JWT）→ 越权测试
- 平台级 admin（company_id=NULL）：操作须显式 target_company_id，服务端校验企业存在 + 平台级身份，否则 40300

## 4. 权限等级继承未定义

- scope 多档（employee/hr/admin）须明确是等级继承而非精确匹配
- 定义：`employee(1) < hr(2) < admin(3)`，可见规则"文档 scope ≤ 用户 scope"
- Milvus 过滤表达式：`company_id == X AND scope_level >= N`
- 越权测试按此设计（hr 读 admin 文档 → 检索不到；hr 读 employee → 可见）

## 5. 状态机显式分支

- `a → b | c → d` 歧义（b 也能进 d？）→ 写 `a → b → c；a → d`
- "任意节点可终局"类宽泛表述必须与转换表精确一致（如 withdrawn 任意非终局节点、rejected 仅决策节点、churned 仅 onboarded 后）
- Offer 流程典型：accept（接受）≠ onboarded（入职），中间允许放弃；两节点须有独立驱动接口

## 6. 内部接口认证无契约

- service token 无来源/格式/轮换/审计/与用户 JWT 区分
- 补契约：环境变量来源、`svc_` 前缀识别、认证中间件按前缀分流互不通用、24h 宽限期轮换、审计 actor_type=service

## 7. 高频遗漏位置（每轮自查必查）

- 前端页面集：API §9 映射有某页（如 Offer 管理），但 ADR/里程碑/详细设计页面表漏掉 → 四文档同步
- 测试编号拆分（F-05→F-05a/b/c）后，API 说明/证据目录/开发指南引用仍写旧编号
- 新增角色/枚举只改一层：employee 角色要进需求用户表、架构安全段、API RBAC、DB users 表
