---
name: hermes-profile-operations
description: "Use when user asks 配置档案改名/profile rename. WinError 5 目录锁修复。"
version: 1.0.0
author: agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [hermes, profile, configuration, rename, winerror5, windows]
    category: software-development
    related_skills: [hermes-troubleshooting, hermes-studio, hermes-agent]
---

# Hermes 配置档案（Profile）操作

管理 Hermes 的配置档案（独立 config/skills/memory 的实例）——创建、重命名、
删除、查看，以及 Windows 上最常见的坑：**重命名被目录锁阻塞**。

## 触发条件

- 用户想新建/重命名/删除配置档案（Profile）
- `hermes profile rename` 报错或 Studio 界面重命名失败
- 错误信息含 `[WinError 5] 拒绝访问` / `Access Denied` 且路径在 `profiles\`
- 群聊需要给 Agent 换名字/换模型（每个 Profile 独立 config.yaml）

## 基本命令

```bash
hermes profile list                # 列出所有配置档案（default + 自定义）
hermes profile show <name>         # 查看某档案路径/模型/gateway 状态
hermes profile create <name>       # 新建（--clone 可复制现有档案）
hermes profile rename <old> <new>  # 重命名
hermes profile delete <name>       # 删除
hermes profile use <name>          # 设为默认
```

配置文件在 `%LOCALAPPDATA%\hermes\profiles\<name>\`（每个档案有自己的
config.yaml / .env / skills / memories）。default 档案在
`%LOCALAPPDATA%\hermes\` 根目录，**不能重命名**（代码强制）。

## ⚠️ 重命名 WinError 5（Windows 最高频坑）

### 症状

```text
Error invoking remote method 'hermes:api': Error: 500; {'detail': '[WinError 5] 拒绝访问。'}
```

CLI 同样失败，`%LOCALAPPDATA%\hermes\logs\errors.log` 显示真实堆栈：

```
PermissionError: [WinError 5] 拒绝访问。: '...\profiles\<old>' -> '...\profiles\<new>'
PATCH /api/profiles/<old> failed   → hermes_cli/web_routers/profiles.py → rename_profile
```

### 根因

**Hermes 桌面版（`Hermes.exe`，位于 `hermes-agent\apps\desktop\...`）** 为每个
Profile 自动启动一个后端进程：

```
python.exe -m hermes_cli.main --profile <name> serve --host 127.0.0.1 --port 0
```

该进程持有 `profiles\<name>` 目录句柄 → Windows 禁止重命名被占用的目录。
`rename_profile()`（`hermes_cli/profiles.py`）只停 gateway **不停 serve**，
所以桌面版开着时 CLI/API 重命名必然失败。

### 关键认知（容易踩）

1. **退出 Hermes Studio ≠ 退出 Hermes.exe 桌面版**——两个独立应用。
   Studio 在 `D:\Program Files\Hermes Studio\`，桌面版在
   `hermes-agent\apps\desktop\release\win-unpacked\Hermes.exe`。
2. 桌面版会**自动重启**被杀掉的 serve 进程（新 PID）——只杀不马上改名没用。
3. `hermes serve --status` 只追踪 default dashboard server，**看不到**
   各 profile 的 serve 进程。要用 Win32_Process 命令行过滤找。

### 修复（两条路）

**路 A（推荐，快）：杀 serve + 立即重命名，一条命令内完成**

```bash
# 1. 杀掉持有目录的 serve 进程
powershell -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'profile <name> serve' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"

# 2. 立刻（300ms 内）执行重命名，抢在自动重启前
hermes profile rename <old> <new>
```

**路 B（稳）：完全退出 Hermes.exe 桌面版**（所有 Hermes.exe 进程），
再在终端里 `hermes profile rename <old> <new>`。

### 验证

```bash
hermes profile list        # 新名字出现
ls ~/.local/bin/<new>.bat  # 包装脚本已更新（旧的 <old>.bat 被移除）
```

注意：重命名后，桌面版里原来的 `<old>` Agent 会失效，需重启桌面版后重新添加。

## 坑位速查

| 现象 | 原因 | 处理 |
|------|------|------|
| rename 报 WinError 5 | serve 进程锁目录 | 杀 serve + 立即 rename |
| 杀了 serve 还是失败 | 桌面版自动重启了 | 完全退出 Hermes.exe 再改名 |
| 找不到 serve 进程 | `serve --status` 不显示 profile 进程 | 用 Win32_Process 过滤 `profile <name> serve` |
| 想把 default 改名 | 不支持 | 建新档案 + `hermes profile use` |
| Studio 界面改名失败但 CLI 成功 | UI 走了 PATCH API，同样被锁 | 先杀 serve 再在 UI 操作 |

## 相关技能

- `hermes-troubleshooting` — 桌面连接、gateway、锁文件等通用故障
- `hermes-studio` — 群聊添加 Agent、popout、Studio UI 操作
- `hermes-agent` — Hermes 全局配置与 CLI 参考
