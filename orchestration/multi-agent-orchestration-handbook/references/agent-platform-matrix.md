# 超级大厂 Agent 平台对比

Google · Meta · Microsoft · Amazon · Alibaba Cloud · ByteDance — 2025-2026

## 核心架构对比

| 维度 | Google | Meta | Microsoft | Amazon | Alibaba | ByteDance |
|:-----|:-------|:-----|:----------|:-------|:--------|:----------|
| 编排范式 | ADK + A2A Agent Card | Llama Stack Session/Turn | SK Plugin + AutoGen GroupChat | Supervisor + Swarms | Leader-Worker DAG | LangGraph + task() |
| 技能管理 | Agent Card (JSON) | Tool Calling + Toolkit | Plugin (KernelFunction) | MCP Tool + Action Group | Skill Registry 热更新 | SKILL.md 动态加载 |
| Agent通信 | A2A 自有标准 | Llama Stack 内部 | SK↔AutoGen 收敛 | A2A + MCP 双协议 | A2A Registry + Matrix | task() + LangGraph |
| 隔离模型 | Vertex AI Serverless | 进程级 Session | AKS 语义内核 | AgentCore microVM | 实例级+RAM角色 | Docker AIO Sandbox |
| 记忆体系 | Vertex AI Memory | Session + Vector DB | SK Memory Store | Bedrock Session | AgentScope 长短记忆 | 跨会话+用户画像 |
| 部署模式 | 全托管 Serverless | 开源自托管 | Azure全托管 | Bedrock全托管 | 容器+云原生 | 本地优先+K8s |
| 模型策略 | Gemini 原生 | Llama 4 自研 | Azure OpenAI | Claude/Llama/Nova | 通义千问 | Model-Agnostic |

## 术语映射

| 概念 | Google | Microsoft | Amazon | Alibaba | ByteDance | Anthropic |
|:-----|:-------|:----------|:-------|:--------|:----------|:----------|
| 技能单元 | Agent Card | Plugin | Action Group | Skill Registry | SKILL.md | Tool (MCP) |
| 编排器 | Root Agent | Orchestrator | Supervisor | Leader | Lead Agent | — |
| 执行器 | Sub-agent | Agent (SK) | Sub-agent | Worker | Sub-agent | — |
| 约束/边界 | Guardrail | Policy/Filter | Guardrail | Constraint Infra | Sandbox Boundary | Hardline/Approval |
| 运行时 | Agent Engine | Kernel Process | AgentCore | Agent Runtime | AIO Sandbox | — |
| 治理层 | Agent Engine Mgmt | SK Orchestration | AgentCore Mgmt | Agent Governance | SuperAgent Harness | — |

## 约束与隔离体系

- **Alibaba Cloud (最完善)** — 四层约束栈：模型网关(Higress) → 运行时行为(Prompt+AgentLoop) → 规则编排(四大Registry+EventBridge) → 可观测(UModel)
- **Amazon Bedrock** — AgentCore microVM 每会话隔离 + Guardrails + Swarm 模式
- **Google Vertex AI** — A2A 协议开创者，Agent Card 声明式发现，Serverless 部署
- **Microsoft** — SK Plugin + AutoGen 收敛，KernelFunction 注册即约束
- **Meta Llama Stack** — Session/Turn 原语，社区驱动技能发现
- **ByteDance DeerFlow** — Docker AIO Sandbox(shell+浏览器+FS)，SKILL.md 格式，MIT 开源
