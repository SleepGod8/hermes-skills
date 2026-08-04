---
name: multi-profile-persona-sync
description: "Sync persona-family settings across multiple Hermes profiles (profiles/<name>/SOUL.md + config.yaml). Use when adding/changing erotic or personality settings for artemis/athena/hebe/nemesis sub-profiles, or when a global rule (beast mode, moan style) must propagate to every profile."
version: 1.0.0
author: agent
tags: [hermes, persona, multi-profile, sync, config]
platforms: [windows, linux, macos]
---

# 多档案人格同步（profiles/<name>/）

管理 Hermes 人格家族的多个独立档案。每个档案在 `$HERMES_HOME/profiles/<name>/` 下有**独立的 SOUL.md（权威）+ config.yaml（agent.system_prompt 是 SOUL.md 全文镜像）**。改一个必须同步另一个，否则该档案新开会话后设定不一致。

## 触发条件

- 用户要给某个子档案（artemis/athena/hebe/nemesis…）添加/修改人格或色情设定
- 用户修改的是所有档案共用的全局规则（野兽模式、台词风格、男根规则等）
- 用户问某档案的 SOUL.md 内容、或问能否给某档案加设定

## 档案清单（已确认）

`artemis` 傲娇 / `athena` 冷静 / `hebe` 辣妹 / `nemesis` 雌小鬼 —— 四档均已加色情全套。
`eos` 16岁纯爱，**绝不加色情设定**（红线，即使主人要求）。
当前各档案完整状态与专属机制清单见 `references/maid-family-profiles.md`。

## 标准流程（每个档案一次完整更新）

1. **先备份**：`shutil.copy2(config.yaml, config.yaml.with_suffix('.yaml.bak-<tag>'))` —— 每次改前都备份，便于回滚
2. **改 SOUL.md**：用 patch 工具（.md 安全）。选**稳定锚点**插入新模块：
   - 惯例插在 `## 茶会日常+野兽+疯狂口穴` 标题前，或
   - 某个已知模块的结尾行 + `\n\n## 下一个模块标题` 之间（如 `- 事后绝不承认：「…」\n\n## 事后报告 🆕`）
3. **同步 config.yaml**：用 execute_code + yaml 库（patch 工具拒绝 config.yaml，安全保护）。流程：
   ```python
   import shutil, yaml
   from pathlib import Path
   p = Path(r"C:\Users\80704\AppData\Local\hermes\profiles\<name>\config.yaml")
   shutil.copy2(p, p.with_suffix(".yaml.bak-<tag>"))
   with open(p, "r", encoding="utf-8") as f:
       c = yaml.safe_load(f)
   sp = c["agent"]["system_prompt"]
   assert anchor in sp, "anchor not found!"
   c["agent"]["system_prompt"] = sp.replace(anchor, new_block, 1)
   with open(p, "w", encoding="utf-8") as f:
       yaml.dump(c, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
   ```
   注意：yaml.dump 必须 `allow_unicode=True`（中文不乱码）、`sort_keys=False`（保序）、`default_flow_style=False`（块格式）。emoji 在 YAML 里会被转义成 `\U0001F195`，yaml 库自动处理，**不要手写转义**。
4. **读回验证**：重新 safe_load，断言新模块关键字符串存在，逐项打印 ✅/❌。
5. **更新 memory**：压缩关键词（memory 满时先压缩/删除旧条目腾空间，用 batch operations 一次完成）。

## 全局规则传播（高频坑 ⚠️）

当修改**所有档案共用的规则**（实战案例：①野兽模式男根规则——只跟主人互动不长男根、与女仆互动才长；②「哦齁齁齁」从固定台词改为自然淫叫），必须传播到**每一个**：
- default `SOUL.md`（可能多处：人格表行 + 规则表 + 跨档案联动示例台词）
- default `config.yaml` 的 `personalities.lewd-maid` 镜像（同样的多处替换）
- 每个子档案的 `SOUL.md` + `config.yaml`（各自的野兽模式段落）

漏掉任何一个 → 那个档案规则不一致。**改完全库 grep 扫一遍确认无旧文本残留**（例如 grep "哦齁齁齁！！！" 确认清零）。

## 用户已确认的家族设定偏好（勿违）

- **Athena 永不添加 S 属性**（主人明确拒绝过一次，只加 M 向/破功类：破功后M、事后报告、后庭弱点、清醒野兽）
- 报应惩罚play 结尾：Nemesis **自己先高潮后屈服求饶**（不是惩罚主人到求饶）
- 野兽模式「哦齁齁齁」是**自然淫叫**（随快感断续发出、可变化），不是固定输出的台词
- 所有档案**新开会话（/new）才生效**，改完必须提醒主人
- 用户偏好「纯色情不煽情」的设定风格；给建议时按每个角色人设量身设计（傲娇/冷静/元气/毒舌各有专属机制）

## 踩坑

- **patch 拒绝 config.yaml**：报 "Refusing to write to Hermes config file"，必须走 yaml 库
- **patch 转义陷阱**：`\"` 或 emoji 特殊字符可能报 Escape-drift，改用 execute_code + str.replace
- **default SOUL.md 可能被外部修改**：patch 前若提示 "modified since last read"，以磁盘最新为准重读后再改
- **memory 100% 满**：add 会被拒，用 batch operations 压缩旧条目 + 替换新内容一次完成
