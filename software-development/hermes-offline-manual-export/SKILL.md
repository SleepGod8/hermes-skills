---
name: hermes-offline-manual-export
description: "Use when 网络坏了/连不上模型需手动导出 Hermes。直接复制目录做迁移包。"
version: 1.0.0
author: agent
license: MIT
tags: [hermes, migration, offline, manual-export, windows, robocopy]
platforms: [windows]
---

# Hermes 离线手动导出（网络故障/连不上模型时）

场景：电脑网卡/网络被改坏（常见：codex 改代理、Winsock、DNS、固定 IP），Hermes 连不上云端模型 → 无法让 Hermes 自己跑迁移打包。**导出完全不需要联网、不需要模型 API、不需要 Hermes 运行** —— Hermes 全部数据在本地一个文件夹里，手动复制即可。

## 触发条件

- 用户说"另一台电脑网络坏了/网卡被 codex 改坏/连不上云端大模型，Hermes 没法自己导出迁移包"
- 用户说"手动导出 Hermes 的配置和 skill 等文件"
- Hermes CLI 能跑但模型调用失败；或 Desktop 起不来 —— 都直接走文件复制方案
- 关键词：手动导出、离线、网络坏了、连不上模型、迁移包、搬电脑

## 核心原则

1. **复制目录 = 完整导出**。不依赖任何 Hermes 进程/命令/网络。
2. 数据目录默认 `%LOCALAPPDATA%\hermes`；若设了 `HERMES_HOME` 环境变量则以它为准。
3. 复制前**必须退出 Hermes**（Desktop + CLI + 网关），否则 state.db/config 可能被锁或 WAL 未合并。
4. 新机恢复走 `hermes-config-migration` skill（合并优先、路径适配、先过问）。

## 步骤

### 1. 确认目录位置

- 文件管理器地址栏输入 `%LOCALAPPDATA%` 回车 → 找 `hermes` 文件夹
- cmd 查自定义路径：`echo %HERMES_HOME%`（有输出则用那个路径）

### 2. 退出 Hermes（防文件占用）

```
taskkill /F /IM Hermes.exe /IM hermes.exe
```
- 关 Desktop：托盘退出；CLI：exit
- 网卡坏不影响文件系统，退出后即可复制

### 3. 复制整个目录（二选一）

**A. 文件管理器**：右键复制 `hermes` 文件夹 → 粘贴到 U 盘。整目录复制自动带隐藏文件（`.env`）。

**B. cmd robocopy**（更稳，长路径/隐藏文件/占用都不易翻车）：
```
robocopy "C:\Users\<用户名>\AppData\Local\hermes" "F:\hermes-backup" /E /COPY:DAT /R:1 /W:1 /XJ /MT:16
```
- 退出码 0~7 都算成功（1 = 复制完成）
- `/E` 含子目录 `/COPY:DAT` 数据+属性+时间戳 `/R:1 /W:1` 占用文件只重试 1 次不卡死 `/XJ` 跳过 junction `/MT:16` 多线程

### 4. 导出清单（对照）

| 内容 | 文件/目录 | 说明 |
|------|-----------|------|
| 主配置 | `config.yaml` | 模型、平台、MCP |
| 密钥 | `.env`（隐藏） | API key、平台凭据 |
| 人格 | `SOUL.md` | 身份设定 |
| 记忆 | `memories/` | 跨会话记忆 |
| 技能 | `skills/` | 全部 skill |
| 插件 | `plugins/`、`hooks/` | 扩展 |
| 定时任务 | `cron/` | 调度 |
| 登录态 | `auth.json` | OAuth 令牌 |
| 聊天记录 | `state.db`、`sessions/` | 可选，不要可删 |
| 子档案 | `profiles/<名>/` | 每个档案独立 config/SOUL/.env/memories/skills |

实测本机顶层结构（2026-08 确认）：`.env` `auth.json` `config.yaml` `SOUL.md` `memories/` `skills/` `plugins/` `cron/` `hooks/` `state.db` `sessions/` `profiles/`（每档案含 `{config.yaml,SOUL.md,.env,memories,skills,plugins,cron}`）。

### 5. 新机恢复

1. 新电脑装好 Hermes → **先跑一次初始化**生成目录结构 → 退出
2. 备份内容**合并**进 `C:\Users\<新用户名>\AppData\Local\hermes`（只补缺失不覆盖同名）
3. 旧 `config.yaml` 的 `mcp_servers` 等路径指向旧电脑（`C:\Users\旧用户名\...`），需改路径
4. 详细合并流程 → **加载 `hermes-config-migration` skill**（先过问、MD5 比对、路径适配、`hermes profile show` 验证）

## 网卡修复三板斧（救不回来前的快速尝试）

codex 改坏的网络十有八九是代理/Winsock/DNS，不是硬件：

1. 管理员 cmd：
   ```
   netsh winsock reset
   netsh int ip reset
   ipconfig /flushdns
   ```
   重启电脑
2. 检查代理：设置 → 网络和 Internet → 代理 → 全关；环境变量 `http_proxy`/`https_proxy`/`ALL_PROXY` 是否被写入
3. 网卡属性 → IPv4 → 自动获取 IP / 自动 DNS（codex 常改固定 IP/DNS）
4. 设备管理器 → 网络适配器 → 卸载网卡 → 扫描检测硬件改动重装驱动
5. 救不回来 → 手机 USB 共享网络可临时联网；但导出不需要联网，U 盘直接复制即可

## 验证

- 复制后 U 盘 `hermes-backup\` 里应能看到 `config.yaml`、`SOUL.md`、`skills\`、`profiles\` 等
- `ls -a` 确认 `.env`、`auth.json` 也在（隐藏文件）
- 建议对比目录数量：`find hermes-backup -type d | wc -l` vs 原目录
