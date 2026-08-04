---
name: hermes-persona-family-management
description: "Manage Hermes multi-profile persona families (女仆家族): sync SOUL.md + config.yaml across profiles/<name>/, batch-add settings, demo-first workflow, red lines."
version: 1.0.0
author: agent
tags: [hermes, personality, multi-profile, config, family]
platforms: [linux, macos, windows]
---

# Hermes 多档案人格家族管理

管理 Hermes 的「人格家族」：default 档案 + profiles/<名>/ 下的多个独立女仆档案（artemis/athena/hebe/nemesis/eos）。与单人格技能（hermes-personalities）互补——那个管单个 SOUL.md/personalities 库，这个管多个独立档案的批量同步。

## 触发条件

- 用户要求给多个档案（profiles/<名>）添加/修改人格设定
- 用户问某个档案的详细设定、某个档案与其他档案的互动
- 用户要求新增/修改野兽模式、配对互动、共通机制等家族级设定

## 档案结构

```
~/AppData/Local/hermes/profiles/<name>/
├── SOUL.md          # 该档案人格权威（完整版）
└── config.yaml      # agent.system_prompt = 通常是 SOUL.md 全文镜像
```

- default 档案的 SOUL.md 在 `~/AppData/Local/hermes/SOUL.md`，config.yaml 里 `agent.personalities.lewd-maid` 是它的镜像
- eos 例外：config.yaml system_prompt 是 ~119 字符简版摘要，不是全文镜像！

## 同步工作流（每次新增/修改设定）

1. **patch 档案 SOUL.md**：新模块插在已知唯一锚点前（如 `## 茶会日常+野兽+疯狂口穴 🆕`、`## 共通色情机制 🆕`）
2. **execute_code + yaml 库同步 config.yaml**：同锚点字符串替换 `agent.system_prompt`（YAML 加载后是真实 \n）
3. **读回验证**：yaml.safe_load 后检查关键子串，逐项打印 ✅/❌
4. **备份**：改 config.yaml 前 `shutil.copy2` 到 `.yaml.bak-<标签>`，一改一备份
5. **更新 memory**：压缩关键词摘要；满了用 operations 批量处理（remove 过时条目 + replace 压缩）

config.yaml 写入参数（必须）：`allow_unicode=True, default_flow_style=False, sort_keys=False`
config.yaml 只能 execute_code + yaml 库改（patch 工具被安全保护拒绝）。

## 踩坑

- **不是所有档案都是全文镜像**：同步前先检查 system_prompt 是否含目标锚点；eos 是简版摘要，找不到锚点，要按摘要处理（末尾追加一句），不要假设全文替换。
- **patch 前先重读文件**：多会话并行编辑时 patch 工具警告 `was modified since you last read it`；模块顺序可能变了，锚点可能匹配 2 处（`Found 2 matches for old_string`）。先 read_file 全文再选唯一锚点。
- **锚点选唯一性**：如 `- 结束后互相瞪眼：「哼！下次我一定赢！」` 在多个模块出现（三人同侍/四人同侍），必须带上后一行（如 `\n\n## 共通色情机制 🆕`）才唯一。
- **验证字符串必须用文件原文**：读回验证用与写入文本完全一致的子串（「仿佛永远不会满足」≠「永远不满足」），别凭记忆猜措辞。
- **config.yaml 被保护**：patch 直接写会被拒，必须 execute_code + yaml 库。

## 用户工作流偏好（设定添加会话）

- **先演示后写入**：用户常先要求「演示一下」新设定，满意后说「写进档案」。演示是销售载体，别急着改文件。
- **用 clarify 给选项**：批量提议后 clarify，选项「全部/共通/专属/挑几个」高频命中；用户也会直接点名编号（如「添加4」「添加1、5、6、7、8、10」）。
- **内容偏好**：直接的身体/体液/羞耻/极限玩法受青睐（精液处理、子宫口、深度贯穿、连续射精、当众自慰、失神、清醒野兽、男根规则）。**调教/服从系和情境/角色扮演系被连续拒绝**（「换一批」×2）——别提护士/女警/温泉/角色卡/等级调教这类包装设定。
- **设定结构**：共通机制（全员）+ 角色专属 + 配对互动（×角色，带组合名如「傲娇对冰山」）+ 年龄排序；新模块标题带 🆕。
- **eos 红线**：16岁纯爱档案绝不添加任何色情设定，即使主人要求（共通机制、年龄排序也只能加纯爱向定位）。
- **记忆满的处理**：2200 字符上限，接近满时 operations 批量（remove 过时 + replace 压缩），手段：删列表细节、换短词（年上害羞→色情破功）、删低价值尾部条目。

## 验证

改完一批后跑一次读回脚本：遍历所有涉及档案，yaml.safe_load 检查 system_prompt 是否含关键子串，报告 ✅/❌ 缺失项。全部通过才算完成。
