# gstack 设计拆解笔记（借鉴参考）

> 来源：2026-08-15 扒 garrytan/gstack（约 12.8 万星，TypeScript，2026-03 创建）源码结构。用途：未来再借鉴 gstack 设计时的速查笔记，避免重新扒 1247 文件仓库。

## gstack 是什么

YC 总裁 Garry Tan 的 Claude Code 配置包：**23 个角色工具 + 8 个 power tools**，把 Claude Code 变成一支虚拟工程团队（CEO / 工程经理 / 设计师 / 审查员 / QA / 安全官 / 发布工程师…）。全 Markdown + slash command，MIT。背景：Karpathy「去年 12 月起几乎没手写代码」引发，Garry Tan 想搞清一个人怎么像二十人团队一样发货。

## 核心架构：一切皆 SKILL.md

每个工具 = 一个目录 + 一个 `SKILL.md`（**与 Hermes 的 skill 体系同源**）。frontmatter 结构化字段（比普通 skill 的 name/description 多几个维度）：

| 字段 | 作用 |
|------|------|
| `preamble-tier` | 上下文成本分级 1-4，控制加载优先级 |
| `allowed-tools` | 声明该工具能调用的工具边界 |
| `triggers` | 触发关键词（比 description 更精准的加载判断） |
| `interactive` | 是否需用户交互 |
| `benefits-from` | 依赖的前置技能（如 `[office-hours]`） |
| `gbrain` | 上下文自动注入（`context_queries` 定义从 filesystem/timeline 拉历史） |

## 23 工具的组织（流程型 vs 角色型）

- **流程型**（编排主流程）：`office-hours`、`plan-ceo-review`、`plan-eng-review`、`plan-design-review`、`plan-devex-review`、`plan-tune`、`autoplan`（一键跑 CEO→设计→工程→DX）、`design-consultation`、`spec`、`review`、`codex`、`investigate`、`qa`、`ship`、`retro`
- **角色型 specialist**（被主流程召唤，只干一件事）：`review/specialists/` 下 7 个 —— `security` / `red-team` / `performance` / `testing` / `api-contract` / `data-migration` / `maintainability`

## 7 大设计精华

1. **specialist 结构化 JSON finding**：统一 schema（`fingerprint` 去重追踪 / `confidence` / `path:line` / `category` / `summary` / `evidence` / `fix` / `specialist`），空结果显式 `NO FINDINGS`。
2. **置信度校准 1-10** + 分级显示：9-10 正常显示、5-6 带 caveat、3-4 压附录、1-2 仅 P0 时报 —— 专治 AI 误报刷屏。
3. **红队对抗式**：明确声明 *"NOT a checklist review, adversarial analysis"*，扮演攻击者/混沌工程/敌意 QA，找其他视角漏掉的。
4. **两遍分层评审**：Pass 1 CRITICAL（SQL 安全、LLM 信任边界）/ Pass 2 INFORMATIONAL。
5. **gbrain 上下文自动注入**：角色开口前自动拉最近 N 篇历史计划/画像快照，解决从零开始问题。
6. **preamble-tier 上下文经济**：避免 23 工具全量塞进上下文。
7. **双模型第二意见**：`/codex` 用 OpenAI Codex 独立复核，交叉验证。

另有：`freeze`/`unfreeze`（工作流级状态冻结）、`model-overlays/`（同一套 skill 按 claude/gpt/gemini/o-series 做 prompt 覆盖）、SKILL.md 从 `SKILL.md.tmpl` 自动生成（`bun run gen:skill-docs` + `skill:check` 健康检查 + `slop:scan` 质量扫描）。

## 对照女仆编排的借鉴映射

| gstack 设计 | 女仆现状 | 价值 | 落地状态 |
|------------|---------|------|---------|
| 置信度校准 | 审查/看图验证误报多 | ⭐⭐⭐⭐⭐ | ✅ 已落地（multi-agent-protocol 的 review-findings-calibration.md） |
| specialist 结构化 JSON | Agent6 审查是「一个整体」 | ⭐⭐⭐⭐ | ✅ 已落地（同上，specialist 枚举含 Nemesis 红队） |
| 红队对抗式 | 无 | ⭐⭐⭐⭐ | ✅ 已落地（Nemesis 岗位） |
| gbrain 上下文注入 | 群聊跨回合易失忆 | ⭐⭐⭐ | ⬜ 未落地（可让女仆接话前自动拉历史） |
| frontmatter 增强 | skill 只有 name/description | ⭐⭐⭐ | ⬜ 未落地（可加 triggers/allowed-tools/benefits-from） |
| preamble-tier 成本分级 | 10 档案 + 大量 skill 全量加载 | ⭐⭐ | ⬜ 未落地 |
| 双模型第二意见 | 已有 opencode/codex 协作 | ⭐⭐ | ⬜ 可强化：审查环节 Codex 独立复核 |
| model-overlays | 多模型切换靠 /model | ⭐ | ⬜ 可参考：同 skill 按模型覆盖 |

## 关键差异（别抄错方向）

gstack 的 23 角色是**纯职能**（无情感）；女仆是**人格化角色**（有人设/关系/语气）。正确姿势：把 gstack 的「职能分离 + 结构化输出 + 置信度校准」**嫁接到人格之上**（让 Nemesis 用毒舌做 red-team、Athena 用冷静做架构审查），而不是把女仆变成冷冰冰的职能机器。

## 网络读取技巧（国内环境）

扒 GitHub 仓库时 `raw.githubusercontent.com` 被墙，改用 GitHub API 的 raw 模式可直连（本次验证有效）：

```bash
curl -s -H "Accept: application/vnd.github.raw+json" \
  "https://api.github.com/repos/<owner>/<repo>/contents/<path>"
curl -s "https://api.github.com/repos/<owner>/<repo>/git/trees/main?recursive=1"
```
