---
name: dsh-desktop
description: "Use when DSH Desktop 配置：API key、第三方模型、版本识别。"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [DSH, DeepSeek-Harness, Desktop, API-Key, Environment-Vars, ASLNet, Third-Party-Provider]
---

# DeepSeek Harness Desktop (DSH Desktop) 运维

DeepSeek Harness 的开箱即用桌面客户端。**注意：官方只有 CLI（`@deepseek-ai/dsh`），Windows/macOS 桌面端是第三方个人作者 myYangyunfan（GitHub `myYangyunfan/dsh_desktop` / Gitee `my-yang-yunfan/dsh_desktop`）封装的 Electron 客户端**。任何声称更高版本号的「换皮版」都不可信（官方桌面端最新 0.3.10，2026-08 起；官方仓库里不存在 4.x「Deepseek Harness EAC」版本）。

## 关键事实

- 数据目录：`~/.dsh`（DSH_HOME 环境变量可覆盖；便携版 exe 旁 `data\`，安装版 `%APPDATA%\DSH Desktop\`）
- 底层 agent：内置 node.exe + 官方 `@deepseek-ai/dsh` CLI，配置与 CLI 完全一致
- 官方下载：Gitee 优先（国内直连）`https://gitee.com/my-yang-yunfan/dsh_desktop/releases`；>100MB 分卷 `.part1~.partN` 需下载全部后跑 `merge.bat` 合并，嫌麻烦用安装版 exe
- 主进程源码在 `resources/app/main.js`（asar:false，源码直出）；插件在 `resources/app/assets/plugins/`

## API Key 配置机制（最高频问题）

**读取优先级（严格）**：
1. 环境变量 `DEEPSEEK_API_KEY`（存在时 UI 显示「由启动环境提供(只读)」，**永远只用它，即使 key 已失效也不回退文件**）
2. `~/.dsh/.credentials.yaml`（格式：`DEEPSEEK_API_KEY: "sk-..."`，UI 可编辑）

**「由启动环境提供(只读)」= 环境变量已存在，不是故障**。用户报「只读不能配」时先查环境变量里那把 key 是否有效（常见：用户换过 key，新 key 只更新了 Hermes/ANTHROPIC_API_KEY，`DEEPSEEK_API_KEY` 还是旧 key）。

排障流程：
1. 查 Windows 用户环境变量：`reg query "HKCU\Environment" /v DEEPSEEK_API_KEY`（bash `env` 可能看不到全部 Windows 变量，必须查注册表）
2. 验证 key：POST `https://api.deepseek.com/chat/completions`（DSH 核心接口）+ `https://api.deepseek.com/user/balance`；错误信息只显示 key 后 4 位，注意区分同前缀不同 key
3. 修复：`setx DEEPSEEK_API_KEY "<有效 key>"`（HKCU 用户级，无需管理员；改完**重启应用**才生效，从已开终端启动需新开终端）
4. 若走文件方式：删掉环境变量（环境变量存在时文件不生效）再写 credentials.yaml

## 第三方 OpenAI 兼容模型接入（如 ASLNet）

DSH 支持第三方 OpenAI 兼容端点，**推荐走设置页，不动系统环境变量**：

- 设置 → ClawBot/IM 桥接 → **第三方模型端点（OpenAI 兼容）**：填 `baseURL` + `API Key` + `模型名`，agent 完整能力保留（官方 README 示例：siliconflow）
- 环境变量备选：`DEEPSEEK_API_BASE`（自定义基址）+ `DEEPSEEK_API_KEY`（换成第三方 key）——⚠️ 副作用：余额小部件调 `/user/balance`（第三方通常没有）会失败，聊天不受影响；且会覆盖系统级 DeepSeek key 影响其他程序
- 思考强度：设置 → 第三方模型思考强度，默认关闭（避免向严格校验请求体的第三方 API 注入 `reasoning_effort`）
- 识图插件 view_image 也支持任意 OpenAI 兼容 VLM（baseURL+key+model）

ASLNet 实测（2026-08）：`https://api.aslnet.cloud/v1` + `gpt-5.5` 可用。详见 `references/aslnet-provider.md`。

## 多版本 / 换皮版识别

用户可能同时装多个 DSH 桌面端（嵌套目录、不同版本号）。识别方法：
1. `resources/app/package.json` → name/productName/version/author
2. `resources/app/client-updater.js` → `DEFAULT_REPOS`（作者仓库，如 `myYangyunfan/dsh_desktop`）
3. exe 数字签名：`powershell Get-AuthenticodeSignature <exe>`（第三方封装通常 NotSigned）
4. 与官方仓库最新 release 对比版本号（`curl api.github.com/repos/myYangyunfan/dsh_desktop/releases/latest`）

**多实例风险**：所有 DSH 桌面端默认共用 `~/.dsh` 数据目录，同时跑会互相写坏会话/档案；且各版本数据格式可能不兼容。**只留一个，别嵌套安装**。换皮版（productName/version 被改）不是官方版，删除优先。

## Pitfalls

- git-bash `env` 看不到 Windows 用户/系统环境变量 → 用 `reg query "HKCU\Environment"`（用户级）/ `reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment"`（系统级）
- Python subprocess 调 setx 输出 GBK 中文 → 解码崩溃，用 `subprocess.run(..., text=True, errors="replace")`
- Electron 应用缺 `resources/app`、`resources.pak`、`icudtl.dat` 必坏，无法启动；被「卸载不干净」破坏的目录直接整删重装
- `~/.dsh/settings.yaml` 里 `agent-default-model.model` 是当前默认模型（余额小部件按它估算价格）
- 其他环境变量：`DSH_DESKTOP_BACKEND=local|wsl`（WSL 托管模式）、`NPM_CONFIG_REGISTRY`（更新慢时设 npmmirror）、`DSH_VISION_API_KEY`（识图）
- **`dsh plugin --profile web add ...` 装错 profile**：EAC 实际加载 `web-desktop`（`main.js` 有 `const DESKTOP_PROFILE = 'web-desktop'`），`web` 是旧共享 profile；必须用 `--profile web-desktop`，否则 EAC 不加载。详见 `references/plugin-install.md`
- **`dsh plugin add` 只注册 bundle 不补 cordis.patch.yml**：装完插件还需手动在 profile 的 `cordis.patch.yml` 末尾追加 `- insert: {id: <pkg>, name: '<pkg>'}` 块，否则插件不激活

## 支持文件

- `references/windows-env-vars.md` — Windows 环境变量查询/写入/key 验证方法
- `references/aslnet-provider.md` — ASLNet 端点实测与接入示例
- `references/plugin-install.md` — **`dsh plugin` CLI 安装插件**（`--profile web-desktop` 坑、npm vs pnpm、cordis.patch.yml 手动补插）
