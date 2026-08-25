# 幂等契约设计要点（跨文档同步实战沉淀）

来源：AI 人才平台文档套件多轮交叉审查（2026-08）。应用场景：任何带"必填幂等写操作 + worker/自动触发 + 事务"的系统文档套件。

## 1. 幂等键双轨来源（高频踩坑）

| 触发方 | 键来源 | 示例 |
|---|---|---|
| 客户端 HTTP | `Idempotency-Key` Header，UUID v4 | 所有 POST/PUT 写接口 |
| 服务端 worker / graph 内部节点 | 确定性键 `UUID5(NAMESPACE_DNS, f"op:{resource_id}:{param}")` | `auto-submit:{interview_id}:{deadline_at}`、`gen-questions:{interview_id}` |

- worker 不走 HTTP、无客户端 Header，必须用**确定性键**才能防重复调度（worker 重启/重试多次仍命中同一条注册记录）。
- 确定性键的 param 必须用**业务上稳定**的值（如 deadline_at 而非 now()），否则重试生成不同键。
- 注册表加审计字段：`key_source`（client/worker）+ `actor`（user/hr/admin/service/worker）。
- 键格式约束从"严格 UUID v4"放宽为"UUID 格式（客户端 v4 / worker v5）"——否则 Pydantic/DB 校验会拒绝合法 worker 事件。

## 2. 幂等记录事务生命周期（P0 级契约）

状态机：`processing → succeeded | failed`

```
1. 原子抢占：短事务 INSERT（status=processing, processing_token=UUID4,
              processing_expires_at=NOW()+5min）
   - 唯一键冲突 → SELECT ... FOR UPDATE 校验 operation/resource_type/request_hash
   - 指纹不一致 → 40000；一致且租约未过期 → 40900（不重复执行业务）
2. 业务事务：业务资源 + 事件 + 幂等记录终态更新同一事务提交
3. 成功：同事务写 succeeded + response_status/response_body/finished_at，清 token
4. 失败：
   - 确定性失败（参数/权限/状态机/资源不存在）→ 独立终态事务写 failed + 稳定错误响应，永久保留 key
   - 未知异常（DB/网络）→ 先回滚业务事务，再独立事务写 failed(50000/50400)
   - 关键：失败必须保留 key，不能与业务一起回滚，否则重试重复执行
5. processing 重试：租约未过期 40900；过期后
   UPDATE ... WHERE status='processing' AND processing_expires_at < NOW() 原子恢复抢占
   - 旧持有者提交终态必须带 processing_token 条件，防旧执行者覆盖新结果
6. response 可空边界：仅 processing 允许 response_status/response_body 为空，终态必须非空
```

- Redis 只缓存**终态**，不能作为锁或最终状态来源；锁与真相都在数据库。
- 表索引：`uk_idempotency_key`、`idx_idem_resource(resource_type, resource_id)`、`idx_idem_processing(status, processing_expires_at)`。

## 3. 敏感响应加密 envelope（安全红线）

- `idempotency_requests.response_body` 永久保存首次响应；`interview-token` 等接口的响应含 `exchange_token`，**禁止明文落库/落缓存**。
- 规则：含令牌/密钥/敏感字段的响应，先经 `core/crypto.py`（AES-256-GCM）加密为 envelope 再写 MySQL 与 Redis `idem:{key}`；回源时解密后返回。
- 测试用例：发 token 后查注册表与 Redis，断言不含明文、可解密还原。

## 4. Redis 回源目标分类型（勿写"回源数据库"）

- 事件类写操作过期 → 回源 `candidate_events`（按 candidate_id + idempotency_key 判断是否已写）。
- 其他所有必填幂等写操作过期 → 回源 `idempotency_requests`。
- 文档中"过期后回源数据库"这种含糊表述必须写清目标表。

## 5. 跨文档同步清单（改幂等契约时）

- 02-api-design：§1.5 幂等矩阵（每行标 key 来源）、全局幂等键规则、各接口章节（手动/自动两条路径）、错误码表（40900 处理中/乐观锁冲突）。
- 05-database-design：idempotency_requests 字段表 + 生命周期冻结契约、candidate_events/offer_orders 的 idempotency_key 说明、Redis key 表、数据安全设计（加密 envelope）。
- 06-detail-design：Schema（`UUID4 | UUID5` 双轨）、事务一致性伪代码、graph 节点表（自动节点确定性键）。
- REQUIREMENTS：数据表清单、技术栈用途、全局约束条目。
- 03-test-cases：并发抢占/租约恢复/失败终态/失败重试/自动路径幂等/令牌加密，各补一条。
- 版本号 + 修订记录全链同步。

## 6. 陷阱：markdown 表格 patch 双竖线 bug

- 用 patch 工具给 markdown 表格加行时，新行开头容易多一个 `|`，变成 `|| field | ...`，表格渲染断裂。
- 本会话实际踩中 2 次（05-database-design.md 的 idempotency_requests 字段表）。
- 修复后必须 grep `^\|\|` 验证无残留，或回读该表。
