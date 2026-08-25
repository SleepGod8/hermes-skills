# 开工前契约门禁

适用于多文档技术设计套件的最后一轮 P0/P1 审查。

## 1. 外键与租户锚点

API 允许 `candidate_id`/`company_id` 为空时，必须有临时上传或绑定表、所属租户字段和后续绑定流程；否则将外键改为必填。检查 API 可选性、DDL NOT NULL 和租户过滤链是否一致。

## 2. 全部写接口的幂等矩阵

逐个列出创建、上传、异步任务、生成、提交和状态变更接口，标记必填/不适用、Header 约定和永久持久化位置。Redis 只是热缓存；创建类操作不写事件时，使用业务表唯一字段或统一 `idempotency_requests` 表。

如果要求幂等键全局不可复用，不能仅在 candidate_events 上建立局部唯一索引。全局注册表至少保存：idempotency_key、operation、resource_type、resource_id、request_hash、首次响应和 created_at；Redis 过期后必须回源数据库。

## 3. 状态字段语义

遇到同名 status，拆成三类：请求结果、资源档案状态、业务流程状态。推荐显式命名：`result=created`、`candidate_status=active`、`current_stage=applied`，并同步 API、ORM、DDL、需求和测试。

## 4. 枚举与非法测试

API 示例、数据库注释、Pydantic/Literal 和测试必须来自同一公共枚举。非法测试用 `invalid_*` 占位值，不要用仍可能出现在历史文档中的旧业务值制造搜索误报。

## 5. 版本同步

跨文档契约修订后，同时更新所有文档头部版本、日期、修订记录、冻结门禁和交叉引用；只改头部版本而保留“初稿/待冻结”是版本治理缺陷。
