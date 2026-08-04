---
name: hermes-multi-profile-sync
description: Sync persona/personality settings across multiple Hermes profiles (SOUL.md + config.yaml mirrors + memory) — batch workflow, anchor pitfalls, eos summary exception. Use when adding/modifying settings for several profiles at once.
version: 1.0.0
author: agent
tags: [hermes, personality, multi-profile, config, sync]
platforms: [linux, macos, windows]
---

# Hermes 多档案人格同步

批量给多个 Hermes profile（如女仆家族 artemis/athena/hebe/nemesis/eos）添加或修改人格设定时，每个档案要同步两处文件，再配合记忆摘要。本技能是 `hermes-personalities`（单档案/全局人格）的补充——那里管"怎么定义人格"，这里管"怎么把同一份设定同时落到 N 个档案"。

## 触发条件
- 用户要求给多个档案（`profiles/<名>/`）添加设定
- 用户问"添加修改后对应档案会生效吗"（答：**新开会话 /new 才生效**，运行中的旧会话不会热更新）
- 给角色加"共通机制"要同步到全部档案

## 档案结构（每个档案同步两处）
| 档案 | 权威文件 | 镜像位置 |
|------|----------|----------|
| default | `$HERMES_HOME/SOUL.md` | `config.yaml` 的 `agent.personalities.lewd-maid`（完整镜像） |
| artemis/athena/hebe/nemesis | `profiles/<名>/SOUL.md` | `profiles/<名>/config.yaml` 的 `agent.system_prompt`（完整镜像） |
| eos | `profiles/eos/SOUL.md` | `profiles/eos/config.yaml` 的 `agent.system_prompt`（⚠️ **压缩摘要 ~119 字符，非全文镜像**） |

## 标准步骤
1. **先重读目标文件**——文件常被并行会话修改（patch 会警告 `modified since you last read it on disk`），凭记忆的锚点可能失效。曾因记忆中的模块顺序与磁盘不符导致锚点匹配失败。
2. 用 `patch` 改 SOUL.md，锚点必须唯一；报 `Found 2 matches for old_string` 时重读文件、把锚点加长（模块标题 + 上一行内容）。
3. 用 `execute_code` 一次循环同步 N 个 config.yaml：备份 → yaml 加载 → 同锚点 str.replace → yaml.dump → 读回验证。
4. 更新记忆：2200 字符上限；加内容前先 remove 过时条目（如已完成的 watchdog 记录）或压缩条目，用 operations 数组一次原子提交；replace 的 old_text 必须匹配当前实际条目（失败时查看 `current_entries` 再重试）。

## 关键代码模式
```python
import shutil, yaml
from pathlib import Path

hermes_home = Path(r"C:\Users\80704\AppData\Local\hermes")
updates = {
    "artemis": {"anchor": "...唯一锚点...", "blocks": "...新内容..."},
    # ...每档案一条
}
for name, u in updates.items():
    p = hermes_home / "profiles" / name / "config.yaml"
    shutil.copy2(p, p.with_suffix(".yaml.bak-tag"))   # 先备份
    with open(p, "r", encoding="utf-8") as f:
        c = yaml.safe_load(f)
    sp = c["agent"]["system_prompt"]
    assert u["anchor"] in sp, f"{name}: anchor not found!"
    c["agent"]["system_prompt"] = sp.replace(u["anchor"], u["blocks"], 1)
    with open(p, "w", encoding="utf-8") as f:
        yaml.dump(c, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    # 读回验证关键关键词，再继续下一个
```

## 坑（实战验证）
- **锚点不唯一**：patch 模糊匹配报 `Found 2 matches`。解决：重读文件，用更长锚点。
- **文件被外部会话修改**：先重读再 patch。
- **eos 摘要例外**：eos 的 `agent.system_prompt` 不含 SOUL.md 特征锚点（如"记忆偏好"段）。检测锚点不在 system_prompt 中时，改用"末尾追加摘要句"：`sp.rstrip() + "新句。"`。
- **记忆容量**：2200 字符上限，满了会拒绝 replace；先删/压旧条目再批量提交。
- **共通设定只加一次到 default 的 lewd-maid 镜像**，别漏。

## 用户偏好（配置角色色情设定时）
- 流程：给建议清单（分共通/角色专属，带清晰选项）→ `clarify` 选择 → 用户可能要求先"演示"一段效果 → 确认后才批量写入 → 写完后提醒"新开会话（/new）才生效"。
- 被拒方向（"再换一批"）：调教/服从养成系、情境/角色扮演系。
- 接受方向：直接身体/体液/羞耻/极限玩法系；保持"纯色情不煽情"。
- 年龄红线：16 岁 eos 绝不加色情设定，即使主人要求（她只有纯爱+年龄定位）。
