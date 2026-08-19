# FocusFlow 项目工程宪法示例

> 示例用途：作为 `project-constitution-authoring` 的参考样例，展示如何把一份项目规范文档整理成后续 Agent 开发必须遵从的工程宪法。
> 来源：用户上传的 FocusFlow / AI-Powered Productivity Platform 规范文档。
> 注意：这是示例，不是当前所有项目的默认技术栈。

# FocusFlow 项目工程宪法

> 版本：2.1.0-example
> 更新时间：2025-01 来源文档 / Hermes 示例整理
> 适用对象：所有参与 FocusFlow 的 AI Agent / 开发者 / Reviewer

## 0. 使用规则

1. 开发、审查、拆任务、验收前必须先读取本文档。
2. 若 issue、聊天说明或任务书与本文档冲突，先列冲突并请求 Athena/主人确认。
3. 单文件修改优先运行文件级验证；全量 build/test/e2e 只在最终验收或明确要求时运行。
4. 不得泄露 `.env`、API key、token、Cookie 或私钥。

## 1. 项目身份卡

| 项 | 内容 |
|---|---|
| 项目名称 | FocusFlow |
| 一句话定位 | AI 驱动的生产力 SaaS 平台，结合番茄钟、AI 洞察、团队同步与数据分析优化远程团队深度工作。 |
| 业务域 | Productivity SaaS / Team Collaboration |
| 目标用户 | 远程团队、知识工作者、团队管理者 |
| 架构形态 | 微服务 + 事件驱动架构 |
| 规模目标 | Series A startup，目标 10K+ MAU |

## 2. 技术栈

| 层 | 技术 | 版本/约束 | 说明 |
|---|---|---|---|
| 语言 | TypeScript / Python | TS 5.3+ strict，Python 3.12+ | Python 用于 analytics services |
| 前端 | Next.js / React / Tailwind / Radix / Zustand | Next.js 14.2 App Router，React 18.3，TailwindCSS 3.4，Zustand 4.5 | 默认 Server Components |
| 后端 | NestJS / Fastify / FastAPI | NestJS 10.3，Fastify 4.26，FastAPI 0.110+ | API gateway + analytics service |
| 实时 | Socket.io | 4.7 | 团队同步 / 实时状态 |
| 数据库 | PostgreSQL / MongoDB | PostgreSQL 16 + Prisma 5.x，MongoDB 7.0 | MongoDB 用 time-series analytics |
| 缓存 | Redis | 7.2+ | sessions、real-time state |
| 包管理 | pnpm workspace | 9.x | monorepo 管理 |
| AI | OpenAI GPT-4 / LangChain / Pinecone | 按 env 配置 | AI insights / vector DB |
| Observability | OpenTelemetry / Grafana / Sentry | 项目配置为准 | tracing、metrics、error tracking |

## 3. 明确禁止

- 禁止 Redux；使用 Zustand。
- 禁止 Axios；使用 native fetch + retry logic。
- 禁止 Moment.js；使用 date-fns。
- 禁止 class-based React components；只用 function components。
- 禁止 CSS-in-JS；只用 TailwindCSS。
- 禁止 GraphQL；采用 REST + WebSocket 架构。
- 禁止 `any` 逃避类型；用 `unknown` + type guard。
- 禁止把业务逻辑塞进 React components。
- 禁止未批准新增依赖、debug logs、console.logs、注释掉的废代码。

## 4. 架构边界

- Web 使用 BFF pattern。
- 业务逻辑放 service layer，不放 React components。
- 数据访问使用 Repository pattern / Prisma parameterized query。
- Analytics 采用 CQRS 思路。
- 微服务之间采用事件驱动。
- Client Components 只在需要浏览器交互、状态或 effects 时使用；默认 Server Components。

## 5. 代码风格

### TypeScript / React

- TypeScript strict mode，启用 `exactOptionalPropertyTypes`。
- 所有函数必须显式 return type。
- object shape 优先 `type`，少用 `interface`。
- 字面量类型使用 `const` assertions。
- 不使用 default exports，Next.js pages/layouts 例外。

### Python

- 所有函数必须有类型注解和返回类型。
- Pydantic 用于输入/输出校验。
- I/O 全部 async/await。
- mypy strict、ruff、Black。
- 复杂条件可优先使用 pattern matching。

## 6. 安全与权限

- JWT + refresh token。
- RBAC：Admin / Team Owner / Member / Viewer。
- 除 `/auth/*` 和 `/health` 外，API 必须鉴权。
- 团队数据隔离在 middleware 层强制执行。
- Zod 双端校验。
- Prisma 防 SQL 注入。
- bcrypt 12 rounds。
- PII AES-256 加密。
- 必须考虑 audit log、GDPR export/delete。
- 禁止客户端泄露 secrets。

## 7. 性能要求

| 类别 | 指标 |
|---|---|
| Cached API | p50 < 100ms |
| DB queries | p95 < 200ms |
| AI endpoints | p99 < 500ms |
| FCP | < 1.5s |
| LCP | < 2.5s |
| TTI | < 3.5s |
| CLS | < 0.1 |
| Initial bundle | < 200KB gzip |

数据库与缓存规则：

- 禁止 N+1。
- 大于 50 条必须分页。
- 优先 cursor-based pagination。
- Redis session TTL 7 days。
- AI insights cache 24 hours。
- 静态资源走 CDN / edge cache。

## 8. 开发命令与验证策略

### 初始化

```bash
pnpm install
cp .env.example .env
pnpm db:migrate:deploy
pnpm db:seed
pnpm dev
```

### 单服务启动

```bash
pnpm dev:web       # Frontend :3000
pnpm dev:api       # API gateway :8000
pnpm dev:analytics # Analytics :8001
```

### 文件级命令，优先使用

```bash
pnpm tsc --noEmit apps/web/app/dashboard/page.tsx
pnpm prettier --write apps/web/components/Timer.tsx
pnpm eslint apps/web/lib/utils.ts
pnpm vitest run apps/web/__tests__/timer.test.ts
mypy services/analytics/app/insights.py
ruff check services/analytics/app/models.py
```

### 全量命令，谨慎使用

```bash
pnpm typecheck
pnpm test
pnpm build
pnpm test:e2e
```

全量命令耗时较长，只在最终验收、PR 前或用户明确要求时运行。

## 9. 测试策略

- 关键路径覆盖率目标 85%+。
- 外部 API 如 OpenAI、Stripe 必须 mock。
- 集成测试使用 test database。
- 测试描述行为，不描述实现。
- E2E 覆盖核心业务链路，不滥用。

## 10. Git / PR 规范

### 分支命名

```text
feature/FOCUS-123-add-team-insights
fix/FOCUS-456-timer-timezone-bug
hotfix/critical-auth-bypass
chore/upgrade-nextjs-14
```

### Commit 格式

```text
type(scope): description
```

类型：`feat`、`fix`、`docs`、`style`、`refactor`、`perf`、`test`、`chore`。

### PR 前检查

- [ ] `pnpm lint`
- [ ] `pnpm typecheck`
- [ ] `pnpm test`
- [ ] `pnpm build`
- [ ] `pnpm audit`
- [ ] 更新相关文档
- [ ] 删除 debug logs、console.logs、注释废代码
- [ ] 为新功能添加/更新测试

### 需要批准的操作

- force push / rebase shared branches / 修改 git history。
- 直接 push 到 main/develop/staging。
- 删除分支、删除文件或目录。
- 修改 package.json、tsconfig、next.config、`.env`。
- 新增依赖。
- 全量 build/test/e2e。
- 数据库迁移、schema 修改。
- 环境变量、CI/CD、部署。

## 11. Agent 执行协议

1. 先读本文档和任务相关文件。
2. 复述影响范围、关键约束、假设、待确认事项。
3. 先做最小修改方案。
4. 后端：schema / migration / service / endpoint / tests。
5. 前端：component / server action / validation / tests。
6. 优先文件级验证。
7. 必要时补文档、ADR、PR 描述。
8. 最终汇报真实验证结果，不得编造。

## 12. Done Definition

- [ ] 实现范围符合任务，不越界。
- [ ] 遵守技术栈、禁止项、架构边界和代码风格。
- [ ] 核心路径有测试或说明无法测试原因。
- [ ] 执行了对应验证命令并记录真实结果。
- [ ] 文档/API/迁移说明已更新。
- [ ] 无 secrets、debug logs、console.logs、无关格式化。
- [ ] 安全、性能、数据迁移风险已披露。

## 13. 待确认事项示例

| 编号 | 问题 | 建议默认 | 风险 | 需要谁确认 |
|---|---|---|---|---|
| Q1 | AI provider 是否固定 OpenAI GPT-4，还是允许兼容 provider？ | 按 `.env` 与项目配置读取，不写死 provider | 写死会影响成本和国内可用性 | 项目负责人 |
| Q2 | 全量命令是否允许 Agent 自动运行？ | PR 前运行；平时文件级优先 | 全量命令耗时长，影响迭代速度 | Athena/主人 |
