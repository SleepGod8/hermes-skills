---
name: cross-agent-skill-installer
description: "Use when installing skills across AI agents via npx skills."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [skills, cross-agent, npx-skills, hermes, claude-code, codex, opencode, dsh, cordis, universal]
---

# Cross-Agent Skill 安装与管理

`npx skills` 是一个跨 Agent 的技能安装工具（npm 包 `skills`），将一个技能同时安装到本机所有已发现的 AI Agent 中。

## 触发条件

- 用户说「装一个技能/插件到多个 Agent」「跨 Agent 同步技能」
- 用户在 Claude Code / Codex / OpenCode 里也要用 Hermes 已有的某个技能
- 用户提到 `npx skills add` 或 `skills.sh`

## 安装命令

```bash
npx skills add <github-user>/<repo-name> -g -y
```

- `-g`：全局安装（所有 Agent）
- `-y`：自动确认

## 工作原理

### Universal 共享目录

所有 Agent 共享同一份技能文件：
```
~/.agents/skills/<skill-name>/SKILL.md   ← 实际文件
```

各 Agent 通过 symlink 引用：
```
~/.agents/skills/<skill-name>/     ← 实际文件（Universal 格式 SKILL.md）
    ↑ symlink from
    ├── ~/AppData/Local/hermes/skills/<skill-name>     ← Hermes Agent
    ├── ~/.claude/skills/<skill-name>                   ← Claude Code
    └── (各 Agent 各自的 skills 目录)
```

### 支持的 Agent 类型

| Agent | 安装方式 | Skills 目录 |
|-------|---------|------------|
| Hermes Agent | symlink | `~/AppData/Local/hermes/skills/` |
| Claude Code | symlink | `~/.claude/skills/` |
| Codex | universal | `~/.agents/skills/` |
| OpenCode | universal | `~/.agents/skills/` |
| Trae CN | symlink | 各自目录 |
| CodeBuddy | symlink | 各自目录 |
| PromptScript | ❌ 不支持 global install | — |
| **DSH / EAC** | ❌ Cordis 体系不兼容 | 需单独安装 npm 包 |

### ⚠️ DSH EAC 不兼容

DSH 使用 Cordis 插件体系（npm 包 + `cordis.patch.yml` + `dsh.profile.bundles`），与 `npx skills` 的 universal 格式完全不互通。DSH 需要：

1. **npm 包安装**：在 profile 目录 `pnpm add @scope/dsh-plugin-name`
2. **bundles 注册**：`package.json → dsh.profile.bundles` 追加包名
3. **cordis.patch.yml**：追加 `insert` 条目

详见 `dsh-desktop` 技能的 `references/dsh-eac-plugin-install.md`。

## 查看已安装的技能

```bash
# 查看 universal 目录
ls ~/.agents/skills/

# 查看 Hermes 已识别的技能
ls ~/AppData/Local/hermes/skills/

# 查看 Claude Code 已识别的技能
ls ~/.claude/skills/
```

## 安全评估

安装时 `npx skills` 会显示安全评估（Gen / Socket / Snyk）：
- **Safe / 0 alerts**：安全
- **Med Risk**：中等风险（通常是依赖外部网络，不代表恶意）
- 安装后建议阅读 `SKILL.md` 确认权限声明（`allowed-tools`）和 API 端点

## 已知坑

- `npx skills` 的 `raw.githubusercontent.com` 在国内被墙 → 安装可能超时，需代理或镜像
- `PromptScript` 不支持 global install → 安装时会报 failed，正常忽略
- DSH Cordis 插件与 universal 技能是两套体系 → 同一个功能需要两个独立包

## 常见操作

### 给 DSH 单独装一个 universal 技能对应的 Cordis 插件

如果作者同时出了 `@scope/plugin-dsh` npm 包：
```bash
cd ~/.dsh/profiles/web-desktop
pnpm add @scope/plugin-dsh
# 然后手动注册 bundles + cordis.patch.yml
```

### 查看某个技能在哪些 Agent 里可用

```bash
# 检查各 Agent 的 skills 目录
for dir in ~/AppData/Local/hermes/skills ~/.claude/skills; do
    ls "$dir/<skill-name>" 2>/dev/null && echo "✅ $dir" || echo "❌ $dir"
done
```
