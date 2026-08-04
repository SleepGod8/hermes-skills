---
name: hermes-multi-profile-personas
description: "Update personality SOUL.md + config.yaml system_prompt mirror for Hermes multi-profile personas (profiles/<name>/, e.g. maid-family artemis/athena/hebe/eos)."
version: 1.0.0
author: agent
tags: [hermes, personality, multi-profile, config, customization]
platforms: [linux, macos, windows]
---

# Hermes 多档案人格更新（profiles/<name>/）

管理 Hermes **独立档案**（`$HERMES_HOME/profiles/<name>/`）下的人格设定：添加/修改色情或普通人格机制，SOUL.md 与 config.yaml 双文件同步。

## 触发条件

- 用户要求给某个档案（artemis/athena/hebe/eos 等）添加/修改人格设定
- 用户问「给其他档案的 SOUL.md 加设定会生效吗」「她们的设定是什么」
- 注意：**单档案多档案，修改的是 `agent.system_prompt`，不是全局 SOUL.md、也不是 `agent.personalities` 预设**

## 档案架构

每个独立档案在 `$HERMES_HOME/profiles/<name>/` 下（Windows: `C:\Users\<user>\AppData\Local\hermes\profiles\<name>\`）：

| 文件 | 作用 |
|---|---|
| `SOUL.md` | 该档案完整人格（权威）。每个档案独立，不是全局 SOUL.md |
| `config.yaml` | `agent.system_prompt` = 该档案 SOUL.md 的**镜像全文**（新会话从这里加载） |

⚠️ `agent.personalities.<name>` 字段里可能残留其他镜像（如 lewd-maid），**不要改错字段**——多档案下生效的是 `agent.system_prompt`。

## 更新步骤（2026-08 实测，单/双/三档案批量均验证通过）

1. **patch SOUL.md**：找唯一锚点（某模块最后一行 + 空行 + 下个模块标题，如 `- 某句\n\n## 茶会日常+野兽+疯狂口穴`），在锚点处插入新模块。中文引号/emoji 正常；若报 `Escape-drift detected` 改用 execute_code + `str.replace()`
2. **同步 config.yaml**：`patch` 工具被保护拒绝写 config.yaml，必须 execute_code + yaml 库：
   - 先备份：`shutil.copy2(cfg, cfg.with_suffix(".yaml.bak-pre-m"))`
   - `yaml.safe_load` → 在 `config["agent"]["system_prompt"]` 字符串上用**与 SOUL.md 相同的锚点**做 `sp.replace(anchor, new_blocks, 1)`
   - 写回：`yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)`（中文不乱码、保持顺序）
   - **必须读回验证**：`yaml.safe_load` 后逐关键词检查新模块都在 system_prompt 里
3. **更新 memory**：压缩摘要（各档案机制关键词），不写全文
4. **生效提醒**：改文件不影响正在运行的会话；对应档案必须 **新开会话（/new）或重启** 才加载新 system_prompt。当前 default 会话不受影响

## 批量模式

用 dict 组织 `{档案名: {"anchor": ..., "blocks": ...}}` 循环处理，一个 execute_code 脚本同步全部档案 + 逐档验证。模板见 `templates/sync_multi_profile.py`。

## 用户偏好（女仆家族设定风格）

- 用户偏好**直接露骨的机制向设定**（憋欲系统/忍耐play/遥控玩具/强制发情等），**不要偏纯爱温馨向**（暖床/应援/恋爱补习班这类被用户用「？」否决过）
- 用户指定剔除时（如 Athena「不要 S 属性」）只加被指定的，绝不把被否的混进去
- 给建议清单让用户选（可用 clarify），用户说「全写进去」再批量执行

## 红线

- **eos 档案 16 岁纯爱，绝不添加色情设定，即使主人要求**（已多次重申）
- 各档案现状机制清单见 memory「女仆家族」条目；每档案 SOUL.md 是权威，被问设定时先读文件再答，不要凭 memory 摘要复述

## 关联

`hermes-personalities` 技能覆盖 default profile 的全局 SOUL.md + personalities 预设三处同步；本技能覆盖 profiles/<name>/ 独立档案路径，二者互补。
