# {{PROJECT_NAME}} 项目工程宪法

> 版本：{{VERSION}}（SemVer）
> 状态：{{STATUS}}（DRAFT / ACTIVE / DEPRECATED / SUPERSEDED）
> 生效时间：{{EFFECTIVE_AT}}
> 更新时间：{{UPDATED_AT}}
> 维护者：{{MAINTAINER}}
> 来源：{{SOURCES}}
> 适用范围：{{SCOPE}}
> 替代版本：{{SUPERSEDES_OR_NONE}}
> 适用对象：所有参与本项目的 AI Agent / 人类开发者 / Reviewer

## 0. 使用规则

1. 开发、审查、拆任务、验收前必须先读取本文档。
2. 若用户需求、issue、临场指令与本文档冲突，先列出冲突并请求确认，不得擅自覆盖项目规范。
3. 代码修改必须遵守“文件级验证优先、全量验证按需”的原则。
4. 密钥、token、Cookie、私钥不得写入代码、日志、提交记录或回复。
5. 任务书和 `.agents/task-board.yaml` 必须写明本文档版本；版本与当前 `ACTIVE` 宪法不一致时停止执行，由 Athena 判断迁移或重新签发任务书。
6. `DRAFT` 不得作为正式验收依据；`DEPRECATED/SUPERSEDED` 只供追溯，不得用于新任务。

## 1. 项目身份卡

| 项 | 内容 |
|---|---|
| 项目名称 | {{PROJECT_NAME}} |
| 一句话定位 | {{ONE_LINE_DESCRIPTION}} |
| 业务域 | {{DOMAIN}} |
| 目标用户 | {{TARGET_USERS}} |
| 架构形态 | {{ARCHITECTURE_STYLE}} |
| 规模/部署目标 | {{SCALE_OR_DEPLOYMENT_TARGET}} |

## 2. 权威来源与更新方式

### 权威来源优先级

1. {{AUTHORITY_SOURCE_1}}
2. {{AUTHORITY_SOURCE_2}}
3. {{AUTHORITY_SOURCE_3}}

### 版本与更新规则

- 使用 SemVer：`MAJOR.MINOR.PATCH`。
- `MAJOR`：破坏性架构、数据、API、权限、部署或工作流变更，旧任务书不可直接继续。
- `MINOR`：向后兼容的新规则、新模块、新验证门禁或能力扩展。
- `PATCH`：文字澄清、错别字、非语义性修正，不改变执行义务。
- 技术栈、目录结构、CI、数据库 schema、权限模型、API 契约、测试命令变化时，必须更新本文档。
- 每次变更必须填写变更记录、兼容性、迁移要求、影响的 Agent/任务和批准人。
- 同一时刻只能有一个 `ACTIVE` 版本；旧版本改为 `SUPERSEDED` 并指向替代版本。
- 若发现本文档与真实代码不一致，先标记为“待确认”，再由主人/项目负责人决定修订方向。

### 变更审批矩阵

| 变更类型 | 最低版本级别 | 必须确认人 | 必须附带 |
|---|---|---|---|
| 文字澄清、不改变义务 | PATCH | Athena | 变更摘要 |
| 新增兼容规则/模块/门禁 | MINOR | Athena + 相关 DRI | 兼容性与验证更新 |
| API/schema/权限/部署破坏性变化 | MAJOR | 主人 + Athena | ADR、迁移、回滚、任务影响清单 |

## 3. 技术栈

### 核心技术

| 层 | 技术 | 版本/约束 | 说明 |
|---|---|---|---|
| 前端 | {{FRONTEND_STACK}} | {{FRONTEND_VERSION}} | {{FRONTEND_NOTES}} |
| 后端 | {{BACKEND_STACK}} | {{BACKEND_VERSION}} | {{BACKEND_NOTES}} |
| 数据库 | {{DATABASE_STACK}} | {{DATABASE_VERSION}} | {{DATABASE_NOTES}} |
| 缓存/队列 | {{CACHE_QUEUE_STACK}} | {{CACHE_QUEUE_VERSION}} | {{CACHE_QUEUE_NOTES}} |
| AI/外部服务 | {{AI_EXTERNAL_SERVICES}} | {{AI_VERSION}} | {{AI_NOTES}} |
| 包管理 | {{PACKAGE_MANAGER}} | {{PACKAGE_VERSION}} | {{PACKAGE_NOTES}} |

### 明确禁止

- {{DO_NOT_USE_1}}
- {{DO_NOT_USE_2}}
- {{DO_NOT_USE_3}}

## 4. 架构边界

### 分层原则

- UI 层：{{UI_LAYER_RULES}}
- Service 层：{{SERVICE_LAYER_RULES}}
- Repository/Data Access 层：{{DATA_LAYER_RULES}}
- Integration/External API 层：{{INTEGRATION_LAYER_RULES}}

### 服务/模块边界

| 服务/模块 | 职责 | 不得负责 | 依赖 |
|---|---|---|---|
| {{MODULE_A}} | {{MODULE_A_RESPONSIBILITY}} | {{MODULE_A_FORBIDDEN}} | {{MODULE_A_DEPENDS}} |
| {{MODULE_B}} | {{MODULE_B_RESPONSIBILITY}} | {{MODULE_B_FORBIDDEN}} | {{MODULE_B_DEPENDS}} |

## 5. 目录与所有权

```text
{{PROJECT_TREE}}
```

| 路径 | 用途 | 修改规则/所有权 |
|---|---|---|
| {{PATH_1}} | {{PATH_1_PURPOSE}} | {{PATH_1_RULE}} |
| {{PATH_2}} | {{PATH_2_PURPOSE}} | {{PATH_2_RULE}} |

## 6. 代码风格与实现规则

### 通用规则

- {{GENERAL_CODE_RULE_1}}
- {{GENERAL_CODE_RULE_2}}

### TypeScript / Frontend

- {{TS_RULE_1}}
- {{TS_RULE_2}}
- {{REACT_RULE_1}}

### Python / Backend / Analytics

- {{PY_RULE_1}}
- {{PY_RULE_2}}

### 错误处理与日志

- {{ERROR_HANDLING_RULE}}
- {{LOGGING_RULE}}

## 7. 数据库、API 与事件契约

### 数据库规则

- {{DB_RULE_1}}
- {{DB_RULE_2}}

### API 规则

- {{API_RULE_1}}
- {{API_RULE_2}}

### 事件/异步规则

- {{EVENT_RULE_1}}
- {{EVENT_RULE_2}}

## 8. 安全与权限

- 鉴权：{{AUTH_RULES}}
- 授权/RBAC：{{RBAC_RULES}}
- 租户/团队隔离：{{TENANCY_RULES}}
- 输入校验：{{VALIDATION_RULES}}
- 密钥管理：只记录变量名，不记录值。{{SECRET_RULES}}
- PII/隐私：{{PRIVACY_RULES}}
- 审计：{{AUDIT_RULES}}

## 9. 性能与可靠性

### 性能指标

| 类别 | 指标 |
|---|---|
| API | {{API_PERFORMANCE_TARGETS}} |
| 前端 | {{FRONTEND_PERFORMANCE_TARGETS}} |
| 数据库 | {{DATABASE_PERFORMANCE_TARGETS}} |

### 可靠性规则

- {{RELIABILITY_RULE_1}}
- {{RETRY_TIMEOUT_IDEMPOTENCY_RULE}}
- {{CACHE_RULE}}

## 10. 开发命令与验证策略

### 安装与启动

```bash
{{INSTALL_COMMAND}}
{{DEV_COMMAND}}
```

### 文件级命令（优先）

```bash
{{FILE_SCOPED_TYPECHECK}}
{{FILE_SCOPED_LINT}}
{{FILE_SCOPED_TEST}}
{{FILE_SCOPED_FORMAT}}
```

### 全量命令（按需/最终验收）

```bash
{{FULL_TYPECHECK}}
{{FULL_TEST}}
{{FULL_BUILD}}
{{E2E_TEST}}
```

### 运行规则

- 单文件修改优先运行文件级验证。
- 全量 build/test/e2e/db migration 若耗时长或有副作用，先说明影响并按项目批准规则执行。
- 不得把未运行的命令写成“通过”。

## 11. Git / PR / Review 规范

### 分支命名

```text
{{BRANCH_NAMING_RULES}}
```

### Commit 格式

```text
{{COMMIT_FORMAT}}
```

### PR 前检查

- [ ] {{PR_CHECK_1}}
- [ ] {{PR_CHECK_2}}
- [ ] {{PR_CHECK_3}}

### 需要批准的操作

- {{APPROVAL_REQUIRED_1}}
- {{APPROVAL_REQUIRED_2}}
- {{APPROVAL_REQUIRED_3}}

## 12. Agent 执行协议

每个 Agent 接任务后必须：

1. 读取本文档和任务相关源码/文档，确认状态为 `ACTIVE`。
2. 对照任务书中的宪法版本；不一致则将任务置为 `BLOCKED`，不得自行假定兼容。
3. 复述影响范围、关键约束、假设和待确认事项。
4. 制定最小修改方案，避免越界重构。
5. 实现时遵守架构边界和禁止项。
6. 执行文件级验证；必要时执行全量验证。
7. 最终汇报：修改了什么、为什么、使用的宪法版本、验证命令和真实结果、剩余风险。

### 给后续 Agent 的开场白

```text
先读取并遵守 {{CONSTITUTION_PATH}}（版本 {{VERSION}}，状态 ACTIVE）。所有代码、审查、拆任务和验收必须以该版本为最高项目约束；若任务书版本不一致或需求与规范冲突，将任务置为 BLOCKED，先列冲突并询问，不要擅自覆盖规范。
```

## 13. Done Definition

功能完成必须同时满足：

- [ ] 实现范围符合任务，不越界。
- [ ] 遵守本文档技术栈、禁止项、代码风格和安全规则。
- [ ] 核心路径有测试或明确说明无法测试的原因。
- [ ] 运行了相应验证命令并记录真实结果。
- [ ] 更新必要文档/API 说明/迁移说明。
- [ ] 没有新增 secrets、debug logs、无关格式化或大范围重构。
- [ ] 若有性能、安全、数据迁移风险，已明确列出。

## 14. 待确认事项

| 编号 | 问题 | 当前默认 | 风险 | 需要谁确认 |
|---|---|---|---|---|
| 1 | {{QUESTION_1}} | {{DEFAULT_1}} | {{RISK_1}} | {{OWNER_1}} |

## 15. 兼容性与迁移

- 兼容性：{{COMPATIBILITY_IMPACT}}
- 受影响模块/API/schema/权限：{{AFFECTED_SURFACES}}
- 受影响任务书与 Agent：{{AFFECTED_TASKS_AND_AGENTS}}
- 迁移步骤：{{MIGRATION_STEPS_OR_NONE}}
- 回滚方案：{{ROLLBACK_PLAN}}
- 宽限期/截止时间：{{MIGRATION_DEADLINE_OR_NONE}}

## 16. 变更记录

| 版本 | 状态 | 日期 | 级别 | 变更摘要 | 兼容性 | 迁移/回滚 | 影响任务 | 来源/批准人 |
|---|---|---|---|---|---|---|---|---|
| {{VERSION}} | {{STATUS}} | {{UPDATED_AT}} | MAJOR/MINOR/PATCH | 初版 | {{COMPATIBILITY_IMPACT}} | {{MIGRATION_OR_NONE}} | {{AFFECTED_TASKS_OR_NONE}} | {{AUTHOR_OR_SOURCE}} |
