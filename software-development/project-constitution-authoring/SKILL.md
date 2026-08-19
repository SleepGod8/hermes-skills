---
name: project-constitution-authoring
description: "Use when 把项目资料/代码库整理成后续 Agent 必须遵从的项目规范/工程宪法。"
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [project-constitution, agent-development, requirements, code-review, acceptance]
    category: software-development
    related_skills: [project-requirements-analysis, agent-task-spec-authoring, high-reliability-coding-workflow]
---

# 项目工程宪法编写工作流

把一个项目的 README、需求文档、代码库、现有约定或用户口述整理成一份 **后续 Agent 开发必须遵从的项目规范**。目标不是一次性任务书，而是项目级长期约束：后续写代码、审查、拆任务、验收、交接时都先读取并服从它。

## 适用范围

触发场景：

- 用户说“学习/整理这个项目规范”“按这种格式梳理项目规范”“给后续 agent 遵从”。
- 用户上传类似 `agent_example.md`、`AGENTS.md`、项目规范、架构说明、开发手册、代码风格文档。
- 用户要启动一个新项目，希望先生成可复用的 `PROJECT_CONSTITUTION.md` / `AGENTS.md` / `DEVELOPMENT_GUIDE.md`。
- 用户要让多个 coding agent 在同一项目中按统一技术栈、边界、验证、PR 规则工作。

不适用：

- 只给某个 agent 分配一个具体功能任务：优先用 `agent-task-spec-authoring`。
- 只做需求分析不需要形成长期规则：优先用 `project-requirements-analysis`。
- 已进入代码修改阶段：先读取项目宪法，再按对应编码/测试 skill 执行。

## 核心原则

1. **工程宪法优先于临场偏好**：项目规范一旦形成，后续 agent 开发、审查、拆任务、验收都必须先读它；除非用户明确更新宪法。
2. **约束必须可执行**：每条规则要能转化为具体动作、检查命令、禁止项或验收标准；删除空泛口号。
3. **区分事实、推断、待确认**：从文件读到的是事实；根据技术栈补出的合理规范是推断；冲突或缺失必须列入待确认。
4. **文件级验证优先**：提炼项目常用的快速验证命令；全量 build/test/e2e/db migration 等重操作要标明何时运行、是否需批准。
5. **适配后续 Agent**：输出要让另一个 agent 打开就知道技术栈、边界、禁止项、代码风格、测试策略、Git/PR 流程和 Done Definition。
6. **不泄露密钥**：`.env`、token、API key 只记录变量名和用途，不写值。

## 工作流

### 1. 侦察输入源

先判断项目资料类型：

- 代码库：搜索 `package.json`、`pyproject.toml`、`requirements.txt`、`pnpm-lock.yaml`、`next.config.*`、`prisma/schema.prisma`、`docker-compose.yml`、`.github/workflows/*`。
- 文档包：搜索 `README*`、`AGENTS.md`、`docs/**/*`、`需求*`、`架构*`、`规范*`、`*.md`、`*.docx`、`*.pdf`。
- 用户上传单文件：完整读取，提炼其中已经显式写出的规则。

若是代码库，优先读：README/AGENTS → package/pyproject → 架构文档 → 测试/CI 配置 → 关键目录结构。若是文档包，先用 `project-requirements-analysis` 的方法提炼项目性质和模块。

### 2. 抽取规范字段

至少提取并归类：

- 项目定位：一句话说明、业务域、目标用户、规模/部署目标。
- 技术栈：语言、框架、数据库、缓存、包管理器、AI/外部服务、版本要求。
- 禁止项：明确不能使用的库、模式、架构、命令或目录。
- 架构原则：分层、服务边界、数据流、事件流、权限边界、事务边界。
- 代码风格：类型、命名、导出、组件规则、异步规则、错误处理、日志规则。
- 数据与安全：鉴权、RBAC、租户隔离、输入校验、密钥、PII、审计、合规。
- 性能与可靠性：API 指标、前端指标、缓存、分页、N+1、超时、重试、幂等。
- 测试策略：单测/集成/E2E、mock、覆盖率、fixture、测试数据库、文件级命令。
- 开发命令：安装、启动、lint、typecheck、test、build、migration、seed。
- Git/PR：分支命名、提交格式、PR 模板、review checklist、需要批准的操作。
- Agent 工作流：接任务 → 读规范 → 计划 → 实现 → 文件级验证 → 全量验收 → 汇报证据。
- Done Definition：功能、测试、文档、安全、性能、兼容、回滚/迁移说明。

### 3. 处理冲突和缺失

发现冲突时不要自行强行合并，按表格列出：

| 项 | 来源 A | 来源 B | 风险 | 建议默认 | 需用户确认 |

常见冲突：包管理器不一致、测试框架不一致、DB schema 与代码不一致、README 与 CI 命令不一致、文档写 GraphQL 但代码是 REST、角色权限或 DRI 边界不一致。

缺失字段可以补“建议默认”，但必须标注为建议，不得冒充项目既有事实。

### 4. 生成项目宪法文件

推荐文件名按项目习惯选择：

- 仓库根目录已有 `AGENTS.md`：更新或生成 `AGENTS.md`，但保留原有重要规则。
- 没有 agent 入口：生成 `PROJECT_CONSTITUTION.md`，并建议后续 agent 首先读取。
- 若用户指定文件名，以用户指定为准。

主体结构建议使用 `templates/project-constitution-template.md`。正文要包含：

1. 项目身份卡
2. 权威规则与更新方式
3. 技术栈与禁止项
4. 架构边界
5. 目录与所有权
6. 代码风格与实现规则
7. 数据库/API/事件契约
8. 安全与权限
9. 性能与可靠性
10. 测试与验证命令
11. Git/PR/评审规范
12. Agent 执行协议
13. Done Definition
14. 待确认事项

### 5. 让后续 Agent 遵从

交付时给用户一段可复制开场白，例如：

```text
先读取并遵守 <PROJECT_CONSTITUTION.md 或 AGENTS.md>。所有代码、审查、拆任务和验收必须以该文件为最高项目约束；如需求与规范冲突，先列冲突并询问，不要擅自覆盖规范。
```

若是多 agent 项目，可再建议每个子任务书引用该宪法：

```text
本任务受 <PROJECT_CONSTITUTION.md> 约束。只实现本任务边界内文件；禁止修改宪法列出的禁区；完成后按 Done Definition 汇报验证证据。
```

### 6. 验证

创建或更新宪法后至少验证：

- 文件存在且路径正确。
- Markdown 结构完整，关键章节齐全。
- 代码库中的命令与 `package.json` / `pyproject.toml` / CI 配置不明显矛盾。
- 禁止项、需批准操作、验证命令、Done Definition 已明确。
- 待确认事项没有被写成既定事实。

如果没有实际代码库，只能静态验证上传文档的完整性；最终报告中写明“未运行项目命令，因为只有规范文档/用户未要求执行”。

## 输出格式

完成后按以下格式汇报：

```text
结果：已生成/更新项目宪法，路径是 ...
覆盖范围：技术栈、禁止项、架构边界、代码风格、测试、Git/PR、Agent 协议、Done Definition。
关键约束：列 5-10 条最高优先级规则。
待确认：列冲突/缺失项；没有则写“暂无”。
验证：列实际读取的文件、实际写入的文件、实际检查结果；没有运行命令则说明原因。
后续用法：给后续 Agent 的复制开场白。
```

## 版本治理与维护规则

- 工程宪法使用 SemVer，并维护 `DRAFT / ACTIVE / DEPRECATED / SUPERSEDED` 状态；同一时刻只能有一个 `ACTIVE` 版本。
- `MAJOR` 用于破坏性的架构、API、schema、权限、部署或工作流变化；`MINOR` 用于向后兼容的新规则/能力；`PATCH` 仅用于不改变义务的澄清修正。
- 当项目技术栈、测试命令、目录结构、CI、数据库 schema、权限模型或用户决策变化时，必须更新宪法。
- 每次变更必须记录兼容性、迁移步骤、回滚方案、影响任务/Agent 和批准人；破坏性变更须由主人和 Athena 确认。
- 任务书及 `.agents/task-board.yaml` 必须引用工程宪法版本；若与当前 `ACTIVE` 版本不一致，Agent 将任务置为 `BLOCKED`，由 Athena 决定迁移或重新签发。
- 后续 coding/review 中若发现宪法与真实代码矛盾，应先指出矛盾并请求是否修订，而不是静默按旧规范执行。
- 每份宪法必须有版本、状态、生效时间、更新时间、维护者、适用范围、来源和变更记录。

## 支持文件

- `templates/project-constitution-template.md` — 项目工程宪法 Markdown 模板。
- `references/focusflow-project-constitution-example.md` — FocusFlow 示例：把 AI productivity SaaS 项目规范整理成工程宪法的完整样例，可作为后续项目规范生成参考。
