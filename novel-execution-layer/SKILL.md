---
name: novel-execution-layer
description: "正文写作执行层：九阶段门禁式创作 + 两段式写章协议 + 机械质检三件套（黄金三章/去AI味/一致性）。移植自 dsh-novel-writer，融入女仆工作坊岗位制。"
whenToUse: 工作坊进入正文写作阶段时；Dionysus 写章前/后；Eos 审查前；任何章节需要机械质检时。
tags: [novel, writing, quality, workflow]
platforms: [linux, macos, windows]
---

# 正文写作执行层（Novel Execution Layer）

> 来源：dsh-novel-writer v0.1.7（移植）| 融入 novel-workshop-protocol 岗位制 | 版本 v1.0
> 定位：设定决策委员会（W0-W5）的「正文执行机器」。只处理**怎么写**，不处理**写什么**（写什么由 bible + 大纲 + 伏笔表钦定）。

## 0. 与工作坊岗位制的对接

| 原 DSH 角色 | 女仆工作坊对接 | 说明 |
|------------|--------------|------|
| 模型自驱九阶段 | W0 总编调度 | 阶段推进由 W0 派工，不靠模型自觉 |
| 世界书 lorebook | bible.md + 人物卡 + 伏笔表 | 设定唯一来源是 bible，世界书为正文检索加速层 |
| 两段式写章 | Dionysus（W3）执行 | 写章协议见 §3 |
| 质量自检 | 机械脚本 + Eos（W5）审查 | 脚本先跑 → Eos 人工挑刺互补 |
| 修订回退 | W0 派工修订 | 沿用 W3 修订流程 |

## 1. 九阶段流程（按序推进，禁止跳阶段）

`topic(选题) → setting(核心设定) → character(人设) → outline(全书大纲) → volume(分卷) → chapter(分章细纲) → writing(正文) → revision(修订) → done(完本)`

- 工作坊现状：前六阶段已完成（bible v2.5.1 + 三幕骨架 + 分章细纲），当前停在 **writing(正文)** 闸口，等主人拍板启动。
- 进入 writing 前置条件：bible 版本号 + 三幕骨架 + 目标章细纲 + 伏笔表（F01-F29）就绪。
- 阶段产物落盘到 `.novel/reports/` 与正文目录，不用 DSH 的 novel_* 工具（Hermes 无对应工具，靠文件系统 + 脚本质检）。

## 2. 世界书纪律（适配版）

- **写作前必查**：Dionysus 写章前先读 bible 相关章节 + 人物卡 + 伏笔登记（`.novel/` 下文件），确认本章涉及的关键设定。
- **设定即时沉淀**：写作中出现的新关键设定（人物/地名/势力/境界/规则/物品/功法）→ 立即登记 `consistency.py` 账本（`--ledger` 输入 JSON），不落 bible 的进账本待 W0 裁决，禁直接改 bible。
- **确立的关键设定**：主角/体系/核心规则常驻 bible；次要人物/地点用人物卡条目；伏笔用 F 编号登记。
- **伏笔纪律**：F22-F25 由凯恩线正式启用并登记 §6，F26-F29 保持，后续新增从 F30 起号（L266 口径）。

## 3. 正文写作协议（两段式）

1. **准备**：W0 派工 Dionysus → 读 bible 相关章节 + 目标章细纲 + 前文 + 伏笔表。
2. **写章**：Dionysus 直接输出本章正文，遵守约束（字数/视角/禁用词/钩子/语义边界）。
3. **机械质检**：正文落盘后跑 3 个脚本（见 §4），结果附在交付里。
4. **人工审查**：Eos（W5）基于脚本结果 + 人工挑刺（bible 一致性/人物 OOC/伏笔埋设）→ 审查报告。
5. **修订**：W0 分发审查意见 → Dionysus 修订 → 复核通过 → 章归档。
6. **状态登记**：正文可维护书级状态（境界/装备/关系）→ 追加到 `ledger.json`，下一章写作前先查账本。

## 4. 机械质检三件套（scripts/）

| 脚本 | 对应 DSH 模块 | 检测内容 | 用法 |
|------|--------------|---------|------|
| `golden3.py` | diagnose/rules.ts | 字数达标/对话占比/章末钩子/开场钩子/设定灌输/冲突引入，6 维评分 0-100 | `python golden3.py 第1章.md 第2章.md --min 2000 --max 5000` |
| `ai_taste.py` | polish/scanner.ts | AI 味 234 词 5 类匹配，命中明细 + 密度评分（每千字加权） | `python ai_taste.py 章文件.md` |
| `consistency.py` | consistency/detect.ts | 账本覆盖冲突/时间线倒挂/世界书沉淀建议 | `python consistency.py --ledger ledger.json --timeline timeline.json` |

- 词库：`ai_taste_dict.json`（234 词，5 类：转折连接词/万能动作/心理AI腔/形容词堆叠/句末语气）。
- 口径：主口径 totalChars（含标点空白），辅助 cjkChars；对话占比按成对引号内字符数。
- 全部离线纯函数，模型挂了也能跑，评分必出。

## 5. 质量门禁（提交前）

- [ ] golden3.py 各章无 error 级问题（rule-hook/rule-opening）
- [ ] ai_taste.py 评分 < 40（密度可控）；命中处已按策略处理（删/替/改）
- [ ] consistency.py 无 warning 级账本冲突、无时间倒挂
- [ ] 本章完成细纲目标；章末留钩子
- [ ] bible 一致性：无新增设定绕过账本/未裁决直接进 bible
- [ ] Eos 审查通过

## 6. 修订与完本

- 修订：W0 派工 → Dionysus 修订 → W0/Eos 复核 → 归档。
- 完本：全部章节归档后，W0 汇总成稿 + 伏笔回收清单（F 编号逐条对账）。

## 7. 已知边界（移植差异）

- DSH 的 GUI 抽屉/会话驱动/服务端不移植（Hermes 无对应运行时）；只移植纯逻辑与资产。
- DSH 的 JSONPatch 状态更新 → 用 `ledger.json` 追加记录代替（consistency.py 兼容同 schema）。
- DSH 的 lorebook 条目管理 → bible/人物卡/伏笔表 + 账本。
- 提示词模板 62 个在 `prompts/` 目录原样可用，写章/润色/诊断模板可直接引用。
- 世界书样例（SillyTavern 原生 JSON）在 `lorebook-sample/`，可导入主人酒馆 8001。
