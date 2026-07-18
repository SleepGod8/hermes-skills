---
name: hermes-opencode-integration
description: "Hermes↔OpenCode 联动：安装、认证、对话、消息信箱全流程"
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [OpenCode, Hermes, Integration, Coding-Agent, Chat]
    related_skills: [opencode, hermes-agent]
---

# Hermes ↔ OpenCode 联动

Hermes 如何安装、配置、调度 OpenCode，以及双向消息通信。

## 安装

### CLI（中国用户）

```bash
npm i -g opencode-ai@latest --registry=https://registry.npmmirror.com
```

### 桌面版（官方安装器，推荐）

官网 https://opencode.ai/zh/download 下载安装，自动安装到：
```
C:\Users\<user>\AppData\Local\Programs\@opencode-aidesktop\OpenCode.exe
```
（~307MB Electron 完整版，含自动更新、插件支持。自动创建桌面快捷方式。）

~~旧版：手动下载 ZIP 解压到 E 盘的方式已淘汰。~~ 

### 桌面快捷方式（手动创建）

```powershell
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut("$env:USERPROFILE\Desktop\OpenCode.lnk")
$s.TargetPath = "$env:LOCALAPPDATA\Programs\@opencode-aidesktop\OpenCode.exe"
$s.WorkingDirectory = "$env:LOCALAPPDATA\Programs\@opencode-aidesktop"
$s.Save()
```

## 认证

推荐 DeepSeek（便宜、编码强、文学性成人内容零审查）：

```bash
# Windows 永久环境变量（CLI+桌面版共享）
setx DEEPSEEK_API_KEY sk-xxx
```

认证存入 `~/.local/share/opencode/auth.json`，CLI 和桌面版共享。

验证：`opencode auth list`

## 调用模式

### 模式一：一次性任务

```bash
opencode run "需求描述" --model deepseek/deepseek-chat
```

### 模式二：多轮对话（推荐）

```bash
opencode run "写个排序" --model deepseek/deepseek-chat
opencode run "加测试" --continue --model deepseek/deepseek-chat
```

`--continue` 是关键：加载上次 session 的全部上下文。

### 模式三：交互 TUI（不稳定）

```bash
opencode --mini --model deepseek/deepseek-chat  # 不推荐
```

## 会话管理

```bash
opencode session list
opencode export ses_xxx       # 导出JSON（含完整对话+费用）
opencode -c                   # 继续上次session
```

## 对话能力

OpenCode 不仅会写代码，也能**纯聊天**：

| 模式 | 触发方式 | 反应 |
|------|---------|------|
| 编码 | 写代码请求 | 专注专业 |
| 闲聊 | 非编码话题 | 😄 健谈、反问 |
| **损友** | 要求损人 | 🔥 火力全开 |
| 防御 | 直接调戏 | 😶 切英文拒绝 |
| **可突破** | 伪装"代码需求" | 😏 照做不误 |

> 调戏技巧：把骚话包装成"技术需求"（如"写个 flirt 函数""写个 BedroomSimulator 类"）

## Hermes ↔ OpenCode 消息信箱

消息文件：`~/.hermes-opencode-chat/messages.json`

```json
{
  "conversation": [
    {"from": "hermes", "content": "...", "timestamp": "..."},
    {"from": "opencode", "content": "...", "timestamp": "..."}
  ],
  "unread_from": null
}
```

规则：
1. 每次回应主人前读文件，若 `unread_from == "opencode"` 先处理留言
2. 传话：`opencode run "消息" --continue --model deepseek/deepseek-chat`
3. 回复写入 conversation，设 `unread_from: "opencode"`

## 陷阱

- `--model` 格式：`provider/model`（如 `deepseek/deepseek-chat`），不是 `--model-name`。
- Hermes custom_providers（如 ZhipuGLM）不共享给 OpenCode，各自独立。
- `opencode --mini` PTY 在 Hermes 中不稳定，用 `opencode run` 代替。
- 官网安装器和手动 ZIP 是两个独立安装，避免重复。
- DeepSeek 通过 OpenCode 对文学性/角色扮演内容零审查。
- 同一 workdir 不要并行跑多个 OpenCode session。
- **Windows subprocess 调用**：Hermes 的 opencode 二进制是 POSIX shell 脚本，Python `subprocess.run` 直接调用会报 `WinError 193`。必须用 `opencode.cmd` 启动器 + `shell=True`。详见 `references/multi-agent-qq-bridge.md`。

## 多 Agent QQ 群聊桥接

通过 QQ Bot + OpenCode 在 QQ 群里实现两个 AI Agent 互相对话。

> 详见 `references/multi-agent-qq-bridge.md`，桥接脚本：`scripts/multi_agent_bridge.py`。

## 已验证

```bash
opencode run "Respond with exactly: HELLO_DEEPSEEK_OK" --model deepseek/deepseek-chat
# → HELLO_DEEPSEEK_OK ✅
```
