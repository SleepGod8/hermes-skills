---
name: agent-orchestration-patterns
description: Use when 用户问开源 agent 项目(gstack 等)怎么写或要借鉴其编排设计。
version: 1.0.0
author: agent
license: MIT
tags: [orchestration, multi-agent, patterns, gstack, openclaw, borrow]
---

# 多智能体编排模式库（借鉴业界最佳实践）

> 定位：**吸收外部开源项目的最佳实践**，映射到本机多智能体编排体系（女仆家族 / multi-agent 开发协议）。与「how to 编排」类 skill（multi-agent-protocol / group-chat-autonomous-chat）互补——本库负责「从哪抄、抄什么」。

## 触发条件

- 用户问「gstack / OpenClaw / 某开源 agent 项目是什么、怎么写的」
- 用户要「借鉴某个开源项目的设计到女仆 / 多 agent 编排」
- 用户要「研究业界 agent 编排最佳实践」「看看别人怎么搞的」

## 方法论：拆解一个开源 agent 项目

1. **拉文件树**：`curl api.github.com/repos/<owner>/<repo>/git/trees/main?recursive=1`，一眼看清工具定义在哪（通常是 `SKILL.md` / `agents/` / `commands/`）。
2. **定位工具定义**：数清「流程型工具 vs 角色型 specialist」的分布。
3. **读 representative 文件的 frontmatter + 结构**：抓结构化字段（allowed-tools / triggers / preamble-tier / 上下文注入等）。
4. **提炼设计模式**：结构化输出、置信度校准、角色分离、上下文经济、双模型交叉验证……
5. **映射到自己体系**：核心原则是「**职能分离嫁接人格，不丢人设**」——把纯职能设计嫁接到人格化角色之上（让毒舌角色做红队、冷静角色做架构审查），而不是把人设抹平成职能机器。

## 已拆解案例

| 项目 | 规模 | 笔记 |
|------|------|------|
| gstack（garrytan/gstack，YC 总裁的 Claude Code 配置包） | ~12.8 万星 | `references/gstack-design-notes.md` |

## 通用技巧：国内网络读 GitHub 仓库内容

`raw.githubusercontent.com` 常被墙，改用 **GitHub API 的 raw 模式**可直连（本次验证有效）：

```bash
# 读单个文件内容（raw）
curl -s -H "Accept: application/vnd.github.raw+json" \
  "https://api.github.com/repos/<owner>/<repo>/contents/<path>"

# 拉完整文件树（recursive）
curl -s "https://api.github.com/repos/<owner>/<repo>/git/trees/main?recursive=1"

# 仓库元信息（stars/描述/语言）
curl -s "https://api.github.com/repos/<owner>/<repo>"
```

> 注：`git clone` 被墙时另见 `git-china-*` 系列 skill（代理绕过）；这里是「只读拉内容」的轻量替代。

## 借鉴的硬通货（跨项目通用）

1. **结构化 finding + 置信度校准**：`fingerprint`（去重追踪）+ `confidence` 1-10 + 分级显示（低分压附录不刷屏）——专治 AI 误报，几乎任何审查/验证流程都能用。
2. **角色型 specialist 输出统一 JSON schema**，空结果显式 `NO FINDINGS`，不硬凑。
3. **红队 = 对抗式分析**，不是复述检查清单。
4. **上下文经济**：preamble-tier 分级 + 历史上下文自动注入（角色开口前拉最近 N 条相关记录）。

## 落地节奏

- 每次借鉴**先落一个最小补丁验证**（如本次只落地「置信度校准 + 结构化 findings」），跑一轮实战再扩散，不一次铺开全部模式。
- 落地产物写进对应的编排 skill（如 multi-agent-protocol 的 references），本库只保留「来源拆解」。
