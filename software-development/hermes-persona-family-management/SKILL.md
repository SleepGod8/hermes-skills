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
- **lewd-maid 也可能是简版摘要**（实测 ~2355 字符）：只含核心双人格部分，**不含跨档案联动/配对段落**（如「Hermes 的玩弄癖好」× Athena）。改 default SOUL.md 的配对段落时，若 lewd-maid 里找不到对应锚点，直接跳过同步，不要强行写入

## 查询/扮演会话（不写文件）

- **用户问「X的详细设定」**：读对应档案 SOUL.md（`~/AppData/Local/hermes/profiles/<名>/SOUL.md`；default 在 `~/AppData/Local/hermes/SOUL.md`）后按结构展示，别只凭 memory 摘要背——memory 只存压缩关键词，容易漏专属变体细节（如 Athena 的「清醒的野兽」完整条目、Nemesis 的蒙眼/子宫口）。展示时标注 ⭐ 专属条目。
- **用户直接进角色扮演**（「Athena进入清醒野兽模式」「下一位是artemis」「继续挑战」）：立即扮演，不碰任何文件。扮演时保持该档案语气机制（Athena 面不改色+数据报告+耳根红；Nemesis 毒舌卡壳；Artemis 嘴硬到求饶）。
- **多角色排队/点名**：用户点名顺序即剧情顺序（如 年上义务 Hebe→Artemis→Nemesis→Hermes×Iris），每轮结尾留开放决策点（「是否继续？还是摸额头停下？」），等用户裁决，不要自嗨一口气写完。
- 扮演中可临时读 SOUL.md 校准细节（男根规则、开关位置、恢复条件），这不算修改。

## 同步工作流（每次新增/修改设定）

1. **patch 档案 SOUL.md**：新模块插在已知唯一锚点前（如 `## 茶会日常+野兽+疯狂口穴 🆕`、`## 共通色情机制 🆕`）
2. **execute_code + yaml 库同步 config.yaml**：同锚点字符串替换 `agent.system_prompt`（YAML 加载后是真实 \n）。⚠️ **default 档案没有顶层 `agent.system_prompt`**（访问会 KeyError，是正常的）——人格在 `agent.personalities.lewd-maid`，要改的是那个键；profiles/<名>/ 下的档案才是 `agent.system_prompt`
3. **读回验证**：yaml.safe_load 后检查关键子串，逐项打印 ✅/❌
4. **备份**：改 config.yaml 前 `shutil.copy2` 到 `.yaml.bak-<标签>`，一改一备份
5. **更新 memory**：压缩关键词摘要；满了用 operations 批量处理（remove 过时条目 + replace 压缩）

**共通机制/家族级设定的同步目标 = 9 个文件**：default SOUL.md + 四个成人女仆档案（athena/artemis/hebe/nemesis）各 SOUL.md + config.yaml；eos 跳过。批量改时先逐个 `count(锚点)` 确认唯一（必须 ==1），再替换，最后统一读回验证。

config.yaml 写入参数（必须，用 yaml 库时）：`allow_unicode=True, default_flow_style=False, sort_keys=False`
config.yaml 修改方式按存储形态分：
- **转义字符串形态**（system_prompt 以双引号包裹、`\n` 是字面反斜杠-n 两字符）→ **patch 工具可直接改**：old_string/new_string 里写字面 `\n`（即反斜杠+n），锚点取文件中相邻两行（如 `- 组合名：冰山与火焰\n\n### × Iris`）即可唯一命中，lint 会自动跑。改完仍要 yaml.safe_load 验证。
- **块标量/真实换行形态** → patch 会被拒，必须 execute_code + yaml 库改。

## 配对设定跨档案同步（Hermes×Athena 这类）

新增「某女仆 × 某女仆」配对/癖好设定时，要落 **3 个文件**（不是只改目标档案）：
1. 目标档案 SOUL.md（权威）：插到该档案的配对互动部分（如 athena 的 `### × Hermes` 小节末尾）
2. 对应档案 config.yaml system_prompt：同锚点同步
3. default 档案 SOUL.md：在「跨档案联动玩法」下加一节（如 `### Hermes 的玩弄癖好（× Athena）🆕`），内容与档案侧一致
4. memory：一句话摘要（如「Hermes玩弄癖好×Athena：最爱玩她后庭+男根」）

## 踩坑

- **read_file 可能把档案 SOUL.md 误判为二进制**：`file` 显示 UTF-8 text，但 read_file 报 "Binary file - cannot display as text"（疑似 CRLF/BOM 触发）。遇到就用 `terminal` + `python -c "open(p, encoding='utf-8', newline='').read()"` 读全文；`search_files`/rg 对该路径也可能报 os error 3，同样换 python。写入时 `open(..., newline='')` 保留 CRLF。
- **不是所有档案都是全文镜像**：同步前先检查 system_prompt 是否含目标锚点；eos 是简版摘要，找不到锚点，要按摘要处理（末尾追加一句），不要假设全文替换；default 的 lewd-maid 同理（见档案结构节）。
- **patch 前先重读文件**：多会话并行编辑时 patch 工具警告 `was modified since you last read it`；模块顺序可能变了，锚点可能匹配 2 处（`Found 2 matches for old_string`）。先 read_file 全文再选唯一锚点。
- **锚点选唯一性**：如 `- 结束后互相瞪眼：「哼！下次我一定赢！」` 在多个模块出现（三人同侍/四人同侍），必须带上后一行（如 `\n\n## 共通色情机制 🆕`）才唯一。
- **验证字符串必须用文件原文**：读回验证用与写入文本完全一致的子串（「仿佛永远不会满足」≠「永远不满足」），别凭记忆猜措辞。
- **config.yaml 形态决定改法**：转义字符串形态（双引号 + 字面 `\n`）patch 工具直接改成功过；块标量形态被拒，必须 execute_code + yaml 库。改完一律 yaml.safe_load 验证。

## 用户工作流偏好（设定添加会话）

- **先演示后写入**：用户常先要求「演示一下」新设定，满意后说「写进档案」。演示是销售载体，别急着改文件。
- **用 clarify 给选项**：批量提议后 clarify，选项「全部/共通/专属/挑几个」高频命中；用户也会直接点名编号（如「添加4」「添加1、5、6、7、8、10」）。
- **内容偏好**：直接的身体/体液/羞耻/极限玩法受青睐（精液处理、子宫口、深度贯穿、连续射精、当众自慰、失神、清醒野兽、男根规则）。**调教/服从系和情境/角色扮演系被连续拒绝**（「换一批」×2）——别提护士/女警/温泉/角色卡/等级调教这类包装设定。
- **设定结构**：共通机制（全员）+ 角色专属 + 配对互动（×角色，带组合名如「傲娇对冰山」）+ 年龄排序；新模块标题带 🆕。
- **eos 红线**：16岁纯爱档案绝不添加任何色情设定，即使主人要求（共通机制、年龄排序也只能加纯爱向定位）。
- **记忆满的处理**：2200 字符上限，接近满时 operations 批量（remove 过时 + replace 压缩），手段：删列表细节、换短词（年上害羞→色情破功）、删低价值尾部条目。

## 验证

改完一批后跑一次读回脚本：遍历所有涉及档案，yaml.safe_load 检查 system_prompt 是否含关键子串，报告 ✅/❌ 缺失项。全部通过才算完成。
