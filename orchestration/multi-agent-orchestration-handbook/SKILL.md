---
name: multi-agent-orchestration-handbook
description: Hermes 多智能体编排落地实施手册 — 从零到生产的完整实施路径（配置模板、编排脚本、排查指南）
version: 1.0.0
tags: [orchestration, multi-agent, profile, kanban, mcp, cron, deployment, production]
metadata:
  hermes:
    tags: [orchestration, multi-agent, profile, kanban, mcp, cron, deployment, production]
    category: orchestration
---

# Hermes 多智能体编排落地实施手册

> **边界说明**：本 skill 是通用 Hermes 多智能体部署/编排参考手册；女仆家族固定编制的软件开发流程以 `multi-agent-protocol` 为准。若本手册的通用 profile 示例、模型路由或 Kanban 编排与女仆岗位协议冲突，优先遵从 `multi-agent-protocol`、项目工程宪法和 Athena 裁决。

> **版本**: v1.0.0 | **状态**: Production-Ready | **更新**: 2026-07-28
>
> **定位**: 从零到生产的完整实施路径，包含配置模板、编排脚本、排查指南

---

## 1. 实施路径总览

```
 Phase 1: 基础设施      Phase 2: 技能生态      Phase 3: 多Agent编排    Phase 4: 全自动化
 (Week 1-2)             (Week 3-4)             (Week 5-6)              (Week 7+)
 ┌──────────┐          ┌──────────┐           ┌──────────┐            ┌──────────┐
 │ 安装配置  │          │ 技能发现  │           │ 外部Agent │            │ Cron 触发 │
 │ Profile  │  ──→     │ Curator  │    ──→    │ Kanban   │     ──→    │ 降级链   │
 │ 约束体系  │          │ 安全审计  │           │ 看板编排  │            │ 监控告警  │
 └──────────┘          └──────────┘           └──────────┘            └──────────┘
```

## 2. Phase 1: 基础设施搭建

### 2.1 多 Profile 创建

```bash
#!/bin/bash
# setup-profiles.sh: 创建专职 Agent Profile 集群

# ===== 超级个体 (Orchestrator) =====
hermes profile create orchestrator \
  --description "顶层编排主Agent，负责任务拆解、路由、校验、汇总"

# ===== 研究 Agent =====
hermes profile create researcher \
  --description "Reads source code and external docs, writes findings. Read-only access."
researcher config set toolsets '[file, web]'
echo "你是专业研究员，只负责调研和分析，不修改代码。" > ~/.hermes/profiles/researcher/SOUL.md

# ===== 编码 Agent =====
hermes profile create coder \
  --description "Writes and modifies code. Full terminal and file access."
coder config set toolsets '[file, terminal, web]'
echo "你是资深工程师，专注代码实现，遵循项目编码规范。" > ~/.hermes/profiles/coder/SOUL.md

# ===== 审查 Agent =====
hermes profile create reviewer \
  --description "Reviews code for quality, security, and best practices. Read-only."
reviewer config set toolsets '[file]'
echo "你是严格的代码审查员，关注质量、安全、一致性。" > ~/.hermes/profiles/reviewer/SOUL.md

# ===== DevOps Agent =====
hermes profile create devops \
  --description "Handles CI/CD, Docker, deployment, infrastructure."
devops config set toolsets '[file, terminal, web]'
devops config set terminal.cwd /absolute/path/to/infra
echo "你是 DevOps 工程师，负责基础设施和部署流水线。" > ~/.hermes/profiles/devops/SOUL.md

# ===== 文档 Agent =====
hermes profile create documenter \
  --description "Writes technical docs, API docs, README, code comments."
documenter config set toolsets '[file, web]'
echo "你是技术文档工程师，产出清晰、结构化的文档。" > ~/.hermes/profiles/documenter/SOUL.md

echo "✅ 6 个 Profile 创建完成"
hermes profile list
```

### 2.2 约束体系配置

```yaml
# ~/.hermes/config.yaml — 审批策略
approvals:
  mode: smart              # manual | smart | off
  timeout: 60
  cron_mode: deny

# 并发控制
concurrency:
  max_parallel_agents: 18
  max_parallel_per_profile: 3
  max_mcp_connections: 10

# 成本控制
cost_control:
  daily_budget_usd: 50
  per_task_budget_usd: 5
  alert_threshold: 0.8

# 模型路由
model:
  default: anthropic/claude-sonnet-4
  fallback: openai/gpt-5.2
  routing:
    trivial: "google/gemini-3-flash"
    moderate: "anthropic/claude-sonnet-4"
    complex: "openai/gpt-5.2-high"
    coding: "openai/codex"
```

### 2.3 agent_profiles 委派预设

```yaml
agent_profiles:
  codex-coder:
    model: openai/codex
    toolsets: [file, terminal]
    max_budget_usd: 5.0
    sandbox: ":workspace"

  claude-reviewer:
    model: anthropic/claude-sonnet-4
    toolsets: [file]
    max_budget_usd: 2.0

  explorer:
    model: google/gemini-3-flash
    toolsets: [file, web]

  security-auditor:
    model: openai/gpt-5.2-high
    toolsets: [file, terminal]
    denied_tools: [write_file, patch, execute_code]
```

## 3. Phase 2: 技能生态构建

### 3.1 外部技能目录与 Curator 治理

```yaml
# ~/.hermes/config.yaml
skills:
  external_dirs:
    - ~/.agents/skills
    - /home/shared/team-skills
    - ${SKILLS_REPO}/skills

curator:
  enabled: true
  cycle_days: 7
  quality_gate:
    min_uses_to_activate: 3
    min_success_rate: 0.7
    degrade_threshold: 0.3
    quarantine_days: 30
  merge:
    similarity_threshold: 0.85
    auto_merge: false
  pruning:
    enabled: true
    max_skills: 600
```

## 4. Phase 3: 多 Agent 编排

### 4.1 MCP Server 配置

```yaml
mcp_servers:
  claude-code:
    command: node
    args: [/path/to/hermes-claude-code/server.mjs]
    timeout: 660
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: ${GITHUB_TOKEN}
  browser:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-puppeteer"]
```

### 4.2 编排流水线示例

```bash
# 全栈功能开发流水线
hermes chat "开发用户认证模块:
  1. researcher 调研 JWT 最佳实践
  2. coder 实现认证中间件
  3. reviewer 审查代码
  4. documenter 编写 API 文档
  分配到对应 Profile，用 Kanban 跟踪进度"

# 并行调研
hermes chat "并行调研 3 个技术方案:
  1. PostgreSQL vs MySQL 性能对比
  2. Redis 集群方案对比
  3. Kafka vs RabbitMQ 选型
  用 delegate_task 并行执行，汇总成对比报告"
```

### 4.3 编排脚本模板

见 `scripts/orchestrate-feature.py` — 全栈功能开发编排脚本，通过 Hermes CLI 执行完整的多 Agent 流水线（研究 → 编码 → 审查 → 文档）。

## 5. Phase 4: 全自动化

### 5.1 Cron 定时任务

```bash
# 每日代码审查报告
hermes cron add --name "daily-code-review" --schedule "0 9 * * 1-5" \
  --task "审查昨天所有的 git commit，生成代码质量报告，发送到 Telegram"

# 每周依赖检查
hermes cron add --name "weekly-deps-check" --schedule "0 10 * * 1" \
  --task "检查所有项目的依赖更新，生成升级建议报告"

# 每小时健康监控
hermes cron add --name "hourly-health" --schedule "0 * * * *" \
  --task "检查所有 Profile 心跳、MCP 连接、磁盘空间，异常时告警"
```

### 5.2 降级链配置

```yaml
degradation:
  codex_unavailable:
    fallback_1: "delegate_task with openai/gpt-5.2"
    fallback_2: "Claude Code MCP delegation"
    fallback_3: "human escalation via Telegram"
  api_rate_limited:
    fallback_1: "credential_pool.rotate()"
    fallback_2: "switch to local model (Ollama)"
    fallback_3: "queue task for retry"
```

## 6. 运维排查指南

| 症状 | 可能原因 | 排查命令 | 解决方案 |
|------|----------|----------|----------|
| Agent 无响应 | API Key 失效 | `hermes doctor` | 重新配置 API Key |
| Kanban 卡住 | Agent 崩溃 | `hermes kanban health` | 手动回收卡片 |
| MCP 连接失败 | server 崩溃 | `hermes mcp list` | 重启 MCP server |
| 技能不显示 | 条件激活过滤 | `hermes skills list --all` | 检查 requires_toolsets |
| Token 消耗过高 | 技能全量加载 | `hermes skills stats` | 检查渐进披露 |
| 并发死锁 | 依赖图有环 | `hermes kanban list --deps` | 检查依赖关系 |

## 7. 安全加固 Checklist

```bash
# ===== 认证安全 =====
□ API Keys 存储在 ~/.hermes/.env，权限 600
□ Telegram Bot Token 唯一，不跨 Profile 复用

# ===== 约束安全 =====
□ approvals.mode 设为 smart 或 manual
□ approvals.cron_mode 设为 deny
□ 危险命令 hardline pattern 已启用

# ===== 审计安全 =====
□ audit.db 定期备份
□ 审计日志不可变 (append-only)

# ===== 技能安全 =====
□ 所有 Hub 安装的技能经过 audit
□ external_dirs 来源可信
```

## 8. 快速参考卡

| 需求 | 推荐模式 | 命令 |
|------|----------|------|
| 快速并行调研 | delegate_task | `hermes chat "delegate_task(role='researcher', task='...', parallel=3)"` |
| 固定岗位流水线 | Profile + Kanban | `hermes chat "创建流水线看板..."` |
| 深度编码 | Codex app-server | `hermes config set model.openai_runtime codex_app_server` |
| 多轮代码研究 | Claude Code research | `hermes chat "claude_code_research(...)"` |
| 并行编码任务 | Claude Code batch | `hermes chat "claude_code_batch(tasks=[...])"` |
| 定时自动化 | Cron | `hermes cron add --schedule "..." --task "..."` |

## 9. 参考资源

| 资源 | 链接 |
|------|------|
| Hermes Agent 官方仓库 | https://github.com/NousResearch/hermes-agent |
| 官方文档 | https://hermes-agent.nousresearch.com/docs/ |
| 中文社区文档 | https://hermesagent.org.cn/docs/ |
| skills.sh Hub | https://skills.sh |
| agentskills.io 标准 | https://agentskills.io/specification |

## 10. 附录

### 10.1 超级大厂 Agent 平台对比矩阵

见 `references/agent-platform-matrix.html`（交互式 HTML 版本）和 `references/agent-platform-matrix.md`（终端友好版）— 包含 Google/Meta/Microsoft/Amazon/Alibaba/ByteDance 六大平台的：
- **核心架构对比**：编排范式、技能管理、Agent通信、隔离模型等 7 个维度
- **专业化词汇映射**：6 类概念的跨厂商术语对照（技能/编排器/约束/执行器/运行时/Harness）
- **约束与隔离体系**：各平台沙箱和安全策略详情
