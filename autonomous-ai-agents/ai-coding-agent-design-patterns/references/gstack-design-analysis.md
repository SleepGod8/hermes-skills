# gstack（garrytan/gstack）设计拆解

> 来源：2026-08 会话中对 garrytan/gstack 的深度研究（GitHub API 拉取源码）。审查机制（review-findings-calibration.md v1.6-v1.8）即从此项目借鉴，本文件保存「设计来源全景」。

## 是什么

Y Combinator 总裁 **Garry Tan** 开源的 Claude Code 工作流配置（约 12.8 万 stars / 1.9 万 fork，2026-03 创建）。本质：把 Claude Code 变成**虚拟工程团队**——23 个角色工具 + 8 个 power tools，全是 SKILL.md（Markdown 指令），MIT 协议。

**关键事实**：每个工具 = 一个目录 + 一个 SKILL.md + frontmatter（`name`/`description`/`allowed-tools`/`triggers`/`preamble-tier`/`interactive`/`benefits-from`/`gbrain`）。与 Hermes 的 skill 体系**同源**（都是「目录 + SKILL.md + Markdown 指令」）。

## 23 个工具的 4 层结构

| 层 | 工具 |
|----|------|
| Plan-mode（规划评审） | office-hours / plan-ceo-review / plan-eng-review / plan-design-review / plan-devex-review / plan-tune / autoplan / design-consultation / spec |
| Implementation+review | review / codex / investigate / design-review / design-shotgun / design-html / devex-review / qa / qa-only / scrape / skillify |
| Release+deploy | ship / land-and-deploy / canary / landing-report / document-release |
| Setup | setup / setup-browser-cookies / setup-deploy / setup-gbrain / connect-chrome |

## 8 大设计模式（本质一句话）

1. **结构化 findings（JSON）**——每条缺陷一行 JSON，带 `fingerprint`（`file:line:category` 去重追踪）+ `evidence` + `specialist`。
2. **置信度校准**——每条 finding 强制 1-10 分，分级显示（低分压附录，不占主报告）。
3. **Pre-emit verification gate**——finding 进报告前必须逐字引用触发代码行原文，引不出 = 未验证 = 强制降级。专治「字段 X 不存在」类幻觉 FP。
4. **Framework-meta nudge**——ORM/Meta 生成的符号（Django `Meta`、SQLAlchemy `relationship`、Prisma client）先引用 meta-construct，不得武断报「字段不存在」。
5. **两遍分层评审**——Pass 1（CRITICAL：SQL/数据安全 + LLM 信任边界）→ Pass 2（其余）。
6. **review-army（审查军团）**——并行多独立审查者，各自出 finding，汇总交叉验证（多来源独立证实 = 置信度上调，但不过 verification gate）。
7. **model-overlays（模型覆盖层）**——⚠️ **不是「格式适配」，是「模型行为怪癖 + 补偿指令」**：每个模型一张怪癖卡（GPT 的 completion bias→「别列清单动手做」；Sonnet 5 字面理解→「显式说每节都适用」）。
8. **gbrain context_queries**——角色开口前自动注入历史上下文（filesystem glob 拉历史 sessions/design docs/profile）。

## 已借鉴到 multi-agent-protocol 的映射

| gstack 机制 | 落地位置（review-findings-calibration.md） |
|-------------|-------------------------------------------|
| 结构化 findings + fingerprint | v1.6 第 3 节 |
| 置信度校准 + 强制降级 | v1.6 第 4 节 |
| 红队对抗式 | v1.6 第 7 节（归 Agent 6，非开发岗） |
| Pre-emit verification gate | v1.7 第 4.2 节第 5 条 |
| Framework-meta nudge | v1.7 第 4.2 节第 6 条 |
| 两遍分层审查 | v1.8 第 2 节 |

## 未借鉴 + 原因/优先级

- **review-army（审查军团）**：价值 = 并行交叉验证，落地走 Agent 7 候补机制（standby 女仆临时补位审查，Agent 1 分派）。但日常开发 Agent 6 内部轮转已够，属「可选增强」非必需。
- **model-overlays**：本质是「模型行为怪癖补偿」，优先级低——多智能体开发用强模型（DeepSeek/OpenCode），怪癖少；本地弱模型用于 RP 而非结构化输出。轻量做法 = 给 hermes-model-switching 加「切换模型时同步怪癖卡」。

## 关键纠正 / 教训

1. **人格特质 ≠ 职能岗位**：曾把 red-team 审查错分给「毒舌人设」的 Nemesis（开发岗 Agent 5），违反「审查独立于实现」。审查/测试职能只归 Agent 6，毒舌/冷静等人格语气只用于日常聊天。
2. **审查独立于实现是硬约束**：审查者不能审查自己参与实现的代码，否则对抗价值作废。
3. **借鉴外部项目时先拆本质再套用**：model-overlays 的「行为怪癖补偿」本质是读源码才看清的，只看目录名会误判成「格式适配」。
