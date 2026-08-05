---
name: hermes-studio
description: "Hermes Studio桌面版使用：群聊、添加Agent、popout。Use when user asks 群聊。"
version: 1.0.0
author: agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [hermes, desktop, studio, group-chat, room, ui, configuration]
    category: software-development
    related_skills: [hermes-agent, hermes-troubleshooting, coding-agent-provider-setup]
---

# Hermes Studio（Hermes 桌面版）使用与配置

Hermes Studio 是 Hermes Agent 的 **Electron 桌面产品名**（Windows 装在
`D:\Program Files\Hermes Studio\`）。它与 `hermes` CLI **共享同一套**
配置、记忆、技能、会话（config.yaml / .env / skills / state.db）。

## 触发条件

- 用户问 Hermes Studio / Hermes 桌面版怎么用、怎么配置
- 用户问群聊 / 房间 / group chat / 添加智能体
- 输入框变成浮动窗口（popout）想改回固定
- 编程工具（Codex / Claude Code）怎么在 Studio 里启动

## 界面速览

| 区域 | 功能 |
|------|------|
| 左侧边栏 | 会话列表、创建房间（群聊）、搜索、历史、资料 |
| 聊天区 | 主对话区，支持拖拽文件/粘贴图片 |
| 状态栏 | 底部模型选择器 |
| Cmd/Ctrl+K | 命令面板 |
| 设置页 | 显示、模型、语音、网关、记忆、压缩、会话、代理等 |

## 群聊（Group Chat / 房间）

群聊 = 一个**房间（Room）**里多个 Agent + 人类一起聊天。每个 Agent 对应一个
**Profile**（独立人设/模型/技能）或一个 **Coding Agent**（Codex/Claude Code）。

### 配置步骤

1. 左侧边栏点「创建房间」→ 输入房间名称 → 显示"房间已创建"
2. 点「添加智能体」→ 「选择一个配置」→ 从已有 Profile 中选择
   - 可自定义 **Agent 名称**（留空用 profile 名）和 **Agent 描述**
3. 人类成员可设置「你的名称」（群聊昵称）+「自我描述」
4. 房间设置（齿轮）：压缩配置（触发 token 数/最大历史 token/保留最近消息）、
   立即压缩、邀请码设置（生成/轮换）、克隆房间、清理上下文、删除房间
5. 通过**邀请码**可让其他人加入房间（`joinByCode`）

### 群聊支持的 Agent 类型

| 类型 | 说明 |
|------|------|
| Hermes Agent（各 Profile） | 基础成员，一个 Profile 一个 |
| Codex（OpenAI CLI） | 官方支持，群聊中可显示其 workspace diff |
| Claude Code（Anthropic CLI） | 官方支持，同上 |
| Ekko Agent | Hermes 自己的持久记忆 Agent |

更新日志证据（#2264）："Codex、Claude Code 和 Ekko 产生的 workspace diff …
统一适用于实时、恢复和群聊场景"。

**OpenCode / TRAE**：OpenCode 有 Hermes 桥接但非群聊原生成员；TRAE 是独立
IDE 产品，无法接入群聊。

### 群聊行为

- 房间里需要 **@某个 Agent** 它才响应（`requireMentionRoom`）
- 群聊最多展示 **600 条消息**
- 可粘贴文件/图片到群聊
- 人类成员名称与描述按房间独立保存

## 群聊 @all 与 API 限速

**核心结论**：@all N 个 Agent = 瞬间并发 N 个 API 请求，且它们共享同一段群聊
上下文（每个 Agent 各带一份完整历史，Token 消耗翻 N 倍）。是否触发限速取决于
**供应商的限速维度**：

| 供应商 | 限速维度 | 群聊 @all 影响 |
|---|---|---|
| DeepSeek | **只有并发限制**（v4-pro: 500 / v4-flash: 2500，按账号粒度） | 几乎不可能触发 429 ✅ |
| OpenAI / Anthropic / OpenRouter | 按账号统计 RPM + TPM | 同供应商换模型**不能**避开，只有换供应商/账号才行 ❌ |

**真正的开销**：Token 成本（每个 Agent 各带一份上下文）与上下文质量（压缩配置
不合理时响应变差）。缓解：调低群聊压缩阈值、减少 @ 数量、接入本地 Ollama。

**最优解法 — Profile 分散模型**：每个 Profile 有独立的 `config.yaml`
（`%LOCALAPPDATA%\hermes\profiles\<name>\config.yaml`），可配置**不同的
provider + 默认模型**。群聊添加 Agent 时选不同 Profile，@all 请求即分散到
不同供应商/账号的配额池。配置方法：

```bash
hermes profile create <name>            # 新建 Profile
hermes profile show <name>              # 查看
# 直接编辑 profiles/<name>/config.yaml 的 model 段：
#   model:
#     provider: <provider>              # 如 deepseek / custom:agnes
#     default: <model-id>
```

群聊 Agent 列表 = 已有 Profile 列表；想让每个 Agent 用不同模型，先给每个
角色建一个配好模型的 Profile。

## 输入框浮动（popout）↔ 固定

输入框有 docked（固定）↔ floating（浮动）两种状态（`use-composer-popout.ts`）：

- **双击输入框拖拽把手** → 切换固定/浮动
- **把浮动框拖回底部** → 靠近 dock 位置时发光高亮，松手自动吸附
- 状态按标签页/分栏独立记忆

## 编程工具（Coding Agents）

设置/侧栏里的「编程工具」页可管理 Codex / Claude Code：
- 检测安装状态（未安装可一键安装）
- 配置提供商（provider）+ 模型 + 启动方式（原生终端/内置终端）
- 协议支持：OpenAI Chat Completions / Responses / Anthropic Messages

## 更新检查问题

Hermes Studio 的更新检查（设置 → 关于 → 立即检查）若显示红色
"无法连接更新服务器" + "提交 unknown"，根因通常是 **Electron 找不到 git**
（git 装在 D 盘但 Studio 只查 C 盘 + PATH）→ 把 `D:\Program Files\Git\cmd`
加入 Windows 用户 PATH 后**完全重启 Studio**。详见
`coding-agent-provider-setup` 技能（同一节含 git 代理 + shallow.lock 处理）。

## 挖掘 Studio 功能的方法

Studio 的 UI 文案在 `D:\Program Files\Hermes Studio\resources\webui\dist\client\assets\js\zh-*.js`
（压缩 bundle）。用 `grep -o` 搜中文关键词（如"群聊"、"创建房间"）可快速确认
功能存在及配置流程，再配合更新日志（changelog 节）了解版本行为。

## 内置浏览器（Hermes Studio Browser）

Studio 内置 Chromium 浏览器，可通过标准 browser_* 工具或 MCP 工具操作：

### 可用工具

| 工具 | 功能 |
|------|------|
| `browser_navigate` | 打开 URL |
| `browser_snapshot` | 获取无障碍树快照（含 ref 引用） |
| `browser_vision` | 截图+视觉分析 |
| `browser_click` | 点击元素（需 ref） |
| `browser_type` | 输入文字（需 ref） |
| `browser_back` | 返回上一页 |
| `browser_scroll` | 滚动页面 |

### MCP 工具（mcp__hermes_studio_browser__hermes_studio_browser_toolset）

更精细的控制：
- `hermes_studio_browser_tabs` - 管理标签页
- `hermes_studio_browser_navigate` - 导航（open/back/forward/reload/stop）
- `hermes_studio_browser_snapshot` - 获取快照（需 tab_id）
- `hermes_studio_browser_read_text` - 读取页面文本
- `hermes_studio_browser_interact` - 点击/输入/按键/滚动
- `hermes_studio_browser_screenshot` - 截图
- `hermes_studio_browser_console` - 控制台日志

### ⚠️ 安全注意事项

**敏感操作（登录）建议用户自己在浏览器中完成**：
- 不要代替用户输入账号密码
- 飞书/语雀等需要登录的文档：先用 browser_vision 截图分析，再引导用户手动登录
- 登录按钮点击后可能跳转到登录页，需要用户手动完成验证

### 典型场景

```python
# 打开网页并分析
browser_navigate(url="https://xxx.feishu.cn/wiki/xxx")
browser_vision(question="页面上有什么可交互元素？是否有登录框？")

# 读取页面内容
browser_snapshot()  # 获取 ref 引用
browser_click(ref="@e12")  # 点击某个按钮

# 读取登录后的内容
browser_snapshot(full=true)  # 获取完整页面内容
```

## 常见坑

- **不要假设功能不存在** — 先搜 webui zh.js 文案确认，Studio 功能迭代很快
- 群聊里能添加的 Agent 数量 = 已有的 Profile 数量；想多角色先
  `hermes profile create xxx` + SOUL.md
- PATH 修改对已运行的 Studio 不生效，必须完全重启（关掉所有 Hermes Studio.exe）
- **浏览器登录类敏感操作**：引导用户在内置浏览器中手动完成，不要代输入密码
