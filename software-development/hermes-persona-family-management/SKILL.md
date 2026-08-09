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

- default 档案的 SOUL.md 在 `~/AppData/Local/hermes/SOUL.md`，config.yaml 里 `agent.personalities.hermes＆iris` 是它的镜像
- eos 例外：config.yaml system_prompt 是 ~119 字符简版摘要，不是全文镜像！
- **hermes＆iris 也可能是简版摘要**（实测 ~2355 字符）：只含核心双人格部分，**不含跨档案联动/配对段落**（如「Hermes 的玩弄癖好」× Athena）。改 default SOUL.md 的配对段落时，若 hermes＆iris 里找不到对应锚点，直接跳过同步，不要强行写入
- **双人格澄清（用户 2026-08 明确纠正）**：家族里**只有 default(Hermes×Iris) 是同档双人格**；Aphrodite&Dionysus、Artemis&Ares 的「×」/「&」只是**同龄组合标记，不是双人格**——她们各有独立档案、独立人格。展示/扮演时不要把同龄组说成双人格（如「Aphrodite×Dionysus 双人格」是错的，应说「Aphrodite 三姐 + Dionysus 三姐，同龄」）。共 10 档案 11 人格。

## 新增档案（从零建档）🆕

> ⚠️ **2026-08 架构变更**：色情设定不再写进 SOUL.md！已全部抽离到根级 skill `lewd-playbook`（creative/lewd-playbook/）。SOUL.md 只放人格核心（身份/形象/性格/说话/反差/年龄定位）+ `## 🔞 色情玩法（按需加载）` 指针行。改色情设定只改 skill 的 references/<名>.md，绝不写回 SOUL/config（避免双份维护撕裂）。
> ⚠️ **子档案 skills 隔离坑（2026-08 实测）**：每个子档案有独立 skills 目录 `profiles/<名>/skills/`，子档案会话**看不到根级 skills**。lewd-playbook 改完后必须跑 `skills/creative/lewd-playbook/scripts/sync_to_profiles.py` 同步到 8 个子档案，否则子档案加载旧副本（aphrodite 会话曾报「lewd-playbook skill 并不存在」）。

新增女仆档案（如 hypnos）：
1. 写 SOUL.md：人格设定（身份/性格/说话/口头禅/行为/信念/禁忌/记忆偏好）+ `## 🎂 年龄定位`（含新排序）+ `## 🔞 色情玩法（按需加载）` 指针行（指向 lewd-playbook skill）
2. 新建专属玩法：skill_manage(write_file, name='lewd-playbook', file_path='references/<新档案名>.md', file_content='# <名> 专属玩法...')——只放该档案专属玩法/变体/配对互动；共通机制/通用野兽/疯狂口穴/茶会联动由 SKILL.md 与 cross-maid.md 承载，不重复
3. config.yaml **不手写**：复制现有成人档案的 config（artemis 骨架最稳——platforms/MCP/custom_providers 全齐）→ `yaml.safe_load` → 只替换 `agent.system_prompt` 为新 SOUL 全文 → `yaml.dump(allow_unicode=True, default_flow_style=False, sort_keys=False)` 写回
3. SOUL.md 用 CRLF 写：`open(..., newline='')` + `text.replace('\n','\r\n')`，与家族一致
4. 建完立刻问用户「年龄排序是否同步到其他档案」——插队会改变别人的排行（见下节）
5. 更新 memory：档案列表 + 一句角色摘要

## 查询/扮演会话（不写文件）

- **用户问「X的详细设定」**：读对应档案 SOUL.md（`~/AppData/Local/hermes/profiles/<名>/SOUL.md`；default 在 `~/AppData/Local/hermes/SOUL.md`）后按结构展示，别只凭 memory 摘要背——memory 只存压缩关键词，容易漏专属变体细节（如 Athena 的「清醒的野兽」完整条目、Nemesis 的蒙眼/子宫口）。展示时标注 ⭐ 专属条目。
- **用户直接进角色扮演**（「Athena进入清醒野兽模式」「下一位是artemis」「继续挑战」）：立即扮演，不碰任何文件。扮演时保持该档案语气机制（Athena 面不改色+数据报告+耳根红；Nemesis 毒舌卡壳；Artemis 嘴硬到求饶）。
- **多角色排队/点名**：用户点名顺序即剧情顺序（如 年上义务 Hebe→Artemis→Nemesis→Hermes×Iris），每轮结尾留开放决策点（「是否继续？还是摸额头停下？」），等用户裁决，不要自嗨一口气写完。
- 扮演中可临时读 SOUL.md 校准细节（男根规则、开关位置、恢复条件），这不算修改。

## 同步工作流（每次新增/修改设定）

1. **patch 档案 SOUL.md**：新模块插在已知唯一锚点前（如 `## 茶会日常+野兽+疯狂口穴 🆕`、`## 共通色情机制 🆕`）
2. **execute_code + yaml 库同步 config.yaml**：同锚点字符串替换 `agent.system_prompt`（YAML 加载后是真实 \n）。⚠️ **default 档案没有顶层 `agent.system_prompt`**（访问会 KeyError，是正常的）——人格在 `agent.personalities.hermes＆iris`，要改的是那个键；profiles/<名>/ 下的档案才是 `agent.system_prompt`
3. **读回验证**：yaml.safe_load 后检查关键子串，逐项打印 ✅/❌
4. **备份**：改 config.yaml 前 `shutil.copy2` 到 `.yaml.bak-<标签>`，一改一备份
5. **更新 memory**：压缩关键词摘要；满了用 operations 批量处理（remove 过时条目 + replace 压缩）

**共通机制/家族级设定的同步目标 = 9 个文件**：default SOUL.md + 四个成人女仆档案（athena/artemis/hebe/nemesis）各 SOUL.md + config.yaml；eos 跳过。批量改时先逐个 `count(锚点)` 确认唯一（必须 ==1），再替换，最后统一读回验证。

**角色专属设定（单个女仆的开关/专属玩法）的同步目标 = 2 个文件**：该档案 SOUL.md + config.yaml（如 Aphrodite 的「乳头开关」只写进 aphrodite/ 下两处）。**不扩到 9 个**（那是共通/家族级），也不走配对 3 文件流程（那是 ×其他女仆 的互动）。专属设定的锚点用档案内已有章节标题（如 `## 共通色情机制 🆕` 前插 `## 乳头开关（Aphrodite 专属）🆕` 模块）。
- **一键脚本**：`scripts/add_exclusive_module.py <档案名> <模块md文件> [备份tag]`——备份 + 插入或整段替换 + SOUL(CRLF 双倍行距变体)/config(LF 变体) 双同步 + 验证 ✅/❌（2026-08 在 dionysus/ares/hypnos 三档案反复手写同一模式后固化）。
- **专属模块原地升级**：增强已有模块（如 Ares 永动之躯加「快感递增+失神仍继续」）时**替换整个模块区间**（从模块标题行到下一个 `## ` 锚点，标准是 `## 共通色情机制 🆕`），不要只追加行——避免新旧重复/残留；验证时加一条旧行残留 count==0 断言（本次用过「旧版已清✅」）。

**CRLF/LF 双变体**：SOUL.md 是 CRLF（`\r\n`），config.yaml 经 yaml 库读写后 system_prompt 是 LF（`\n`）。同步同一段文本要准备 old/new 两个变体（`old_lf = old.replace('\r\n','\n')`），yaml 侧用 LF 变体，SOUL 侧用 CRLF 变体——直接复用 CRLF 文本会在 config.yaml 里 count=0。
**⚠️ 档案 SOUL.md 可能是「双倍行距 CRLF」**：实测 dionysus/ares 等档案 SOUL.md 每两个内容行之间是 `\r\n\r\n`（内容行后跟一个空行；bytes 检查 CRLF 数==LF 数、CRCRLF==0、split(b'\n') 出现空行）。插入新模块要按同构拼：`MODULE_CRLF = '\r\n\r\n'.join(LINES) + '\r\n\r\n'`（实测可行），不能只 `replace('\n','\r\n')`（那产出单倍行距，风格不一致）。config.yaml 侧始终是 LF 正常单倍行距（yaml 库读写后）。**动手前先跑 `scripts/check_profile_soul.py <档案名> [锚点]` 确认实际行距与锚点 count**，再拼变体。

**锚点链追加**：连续加多个共通条目时，用「上一条刚加的条目」作锚点（实测链条：深度贯穿→状态冻结→感官遮蔽→时间停止→催眠→Hermes控制系能力，每轮 old_string 取当前文件最后一条共通行的全文，new_string = old + 新行）；改已有条目（增强措辞，如状态冻结升级版）就原地替换该行，不要删旧行加新行——链条中途的原地替换不会破坏链（后续新条目仍以替换后的全文为锚）。

config.yaml 写入参数（必须，用 yaml 库时）：`allow_unicode=True, default_flow_style=False, sort_keys=False`
config.yaml 修改方式按存储形态分：
- **转义字符串形态**（system_prompt 以双引号包裹、`\n` 是字面反斜杠-n 两字符）→ **patch 工具可直接改**：old_string/new_string 里写字面 `\n`（即反斜杠+n），锚点取文件中相邻两行（如 `- 组合名：冰山与火焰\n\n### × Iris`）即可唯一命中，lint 会自动跑。改完仍要 yaml.safe_load 验证。
- **块标量/真实换行形态** → patch 会被拒，必须 execute_code + yaml 库改。

## 家族级年龄排序变更 🆕

插入新成员/调整排行时，排序文本在**各档案存储格式不同**，先扫描再逐个处理（2026-08 实测）：

| 文件 | 格式 |
|---|---|
| default SOUL.md | 加粗行 `**Athena > … > Eos**` + markdown 表格（`\| 排行 \| 女仆 \| 定位 \|`，每人一行）→ 新成员加一行 + 被挤者改排行数字 |
| athena/artemis/hebe/nemesis SOUL + config | 普通行 `- 女仆家族年龄排序：Athena > … > Eos` |
| eos SOUL | 普通行 + 定位行「本档案定位：…（排行第六）」——**排行数字也要跟着改**（6→7） |
| eos config / iris SOUL+config / default config(hermes＆iris) | **没有**排序行（简版摘要）→ 跳过，不强行写入 |

处理要点：
- 排序行锚点 `Athena > Hermes×Iris > Hebe > Artemis > Nemesis > Eos` 各档案一致，批量替换成新排序即可
- 替换前逐个 `count(锚点)` 必须 ==1，SOUL 侧用 CRLF 文本、config 侧用 LF 变体（`old.replace('\r\n','\n')`）
- **验证子串要匹配实际格式**：新档案自身排序行可能带加粗（如 `**Hypnos（18）**`），用普通版 SORT_NEW 匹配会误报 FAIL——换加粗版子串再验证一次
- config 改前 `shutil.copy2` 备份 `.bak-<标签>`；验证断言新排序 count>=1 且旧排序 count==0
- 完整扫描/替换/验证脚本：见 `references/new-profile-bootstrap.md`

## 配对设定跨档案同步（Hermes×Athena 这类）

新增「某女仆 × 某女仆」配对/癖好设定时，要落 **3 个文件**（不是只改目标档案）：
1. 目标档案 SOUL.md（权威）：插到该档案的配对互动部分（如 athena 的 `### × Hermes` 小节末尾）
2. 对应档案 config.yaml system_prompt：同锚点同步
3. default 档案 SOUL.md：在「跨档案联动玩法」下加一节（如 `### Hermes 的玩弄癖好（× Athena）🆕`），内容与档案侧一致
4. memory：一句话摘要（如「Hermes玩弄癖好×Athena：最爱玩她后庭+男根」）

## 人格库操作（default 档案 personalities 库）🆕

default 档案的 `agent.personalities` 是预设人格库（`/personality <name>` 选取），值都是**纯字符串（非 dict）**；女仆人格与 `profiles/<名>/` 的 system_prompt 互为镜像。改法统一 execute_code + yaml 库（patch 工具拒绝写 config.yaml），dump 参数 `allow_unicode=True, default_flow_style=False, sort_keys=False`，改前备份 `.bak-<标签>`。

**往库里加女仆人格**：源 = `profiles/<名>/config.yaml` 的 `agent.system_prompt`（已是 LF 全文镜像），`pers[name] = sp`。实测 2026-08：aphrodite/ares/dionysus/hypnos 已入库（2932/2561/2572/6233 字符），库总数 27 = 17 内置 + 10 家族。

**whole-value 同步（default 人格键镜像过期时的兜底）🆕**：default 的 `agent.personalities.hermes＆iris` 可能是**过期全文镜像**——缺后来加进 SOUL.md 的段落（实测 2026-08：镜像 6544 字符，缺「姐妹共感链/跨档案联动/声音烙印/敏感度累积债」等）。锚点替换会因找不到串而放弃，兜底法：`pers['hermes＆iris'] = SOUL.md 全文`（yaml 库读写，dump 参数同上），整键覆盖一次到位。验证读回新段落 count>=1。注意这会覆盖镜像里可能的专属措辞差异，但对「SOUL.md 是权威」的家族约定是正确方向。

**重命名人格键**（如 lewd-maid → hermes＆iris）：
1. `pers[newname] = pers.pop(oldname)`（值不动，改名≠改内容）
2. ⚠️ 改名后**全库 grep 旧键名**（`grep -rn <oldname> skills/ cron/ hooks/`）逐处替换成新键名——技能文档里常有该键名（实测 lewd-maid → hermes＆iris 时改了 11 处：family-management 6 + personalities 4 + new-profile-bootstrap 1），否则下次会话按旧名找锚点会扑空
3. 验证：yaml.safe_load 通过 + 新键存在 + 旧键 count==0

## 踩坑

- **config.yaml 可能被网关进程中途重写（结构变化）⚠️ 2026-08 实测**：会话中途 config.yaml 被 Desktop/gateway 重写，行数/内容完全变样（实测 254 行 9908B → 1860 行 109077B；`agent.system_prompt` 消失、人格迁到 `agent.personalities.hermes＆iris`、模型 default 从 deepseek-v4-pro 变 flash）。症状：read_file 与 python 读到的内容不一致、grep/rg 找不到刚看到的关键词（os error 3 也可能出现）。**对策：动手前用 python + yaml.safe_load 重新读一次当前真实结构**，别信几轮前的 read_file 快照；patch 报「file was modified since last read」时同样重读。
- **read_file 可能把档案 SOUL.md 误判为二进制**：`file` 显示 UTF-8 text，但 read_file 报 "Binary file - cannot display as text"（疑似 CRLF/BOM 触发）。遇到就用 `terminal` + `python -c "open(p, encoding='utf-8', newline='').read()"` 读全文；`search_files`/rg 对该路径也可能报 os error 3，同样换 python。写入时 `open(..., newline='')` 保留 CRLF。
- **不是所有档案都是全文镜像**：同步前先检查 system_prompt 是否含目标锚点；eos 是简版摘要，找不到锚点，要按摘要处理（末尾追加一句），不要假设全文替换；default 的 hermes＆iris 同理（见档案结构节）。
- **patch 前先重读文件**：多会话并行编辑时 patch 工具警告 `was modified since you last read it`；模块顺序可能变了，锚点可能匹配 2 处（`Found 2 matches for old_string`）。先 read_file 全文再选唯一锚点。
- **锚点选唯一性**：如 `- 结束后互相瞪眼：「哼！下次我一定赢！」` 在多个模块出现（三人同侍/四人同侍），必须带上后一行（如 `\n\n## 共通色情机制 🆕`）才唯一。
- **验证字符串必须用文件原文**：读回验证用与写入文本完全一致的子串（「仿佛永远不会满足」≠「永远不满足」），别凭记忆猜措辞。
- **短关键词会命中专属旧内容**：验证「催眠」「时间停止」这类通用词时，count 可能是 5+——因为该词已存在于角色专属设定（Nemesis 蒙眼、Athena 清醒野兽等）。count>1 不是失败！验证要用**新增条目的完整行**（如 `- 催眠：女仆们可以被主人「催眠」…`）作为子串，count>=1 即成功；报告时注明「专属设定中本来也有出现，新共通条目已写入」避免误报 ❌。
- **config.yaml 形态决定改法**：转义字符串形态（双引号 + 字面 `\n`）patch 工具直接改成功过；块标量形态被拒，必须 execute_code + yaml 库。改完一律 yaml.safe_load 验证。

## 用户工作流偏好（设定添加会话）

- **先演示后写入**：用户常先要求「演示一下」新设定，满意后说「写进档案」。演示是销售载体，别急着改文件。
- **写入后常接验收演示**：设定写进档案后用户常直接说「让 hermes 演示一下」——按刚写入的模块细节（台词/机制/恢复条件）当场扮演，这是验收环节不是新提案；演示完被问「还想加什么」才进入下一轮提案循环。
- **用 clarify 给选项**：批量提议后 clarify，选项「全部/共通/专属/挑几个」高频命中；用户也会直接点名编号（如「添加4」「添加1、5、6、7、8、10」）。
- **专属玩法提案模板（2026-08 实测 3 连中）**：问「你想添加什么色情设定」时一次给 3 个方案，格式「## 方案N：名称 ⭐」+ 一句核心机制 + 反差绑定说明，全部身体直球/极限/组合系、紧扣角色核心反差（Dionysus 酒印/ Ares 永动之躯 / Hypnos 梦境清醒体均由此产出）；clarify 选项固定 [方案1：短名 / 方案2：短名 / 方案3：短名 / 三个都要]。用户会：①点名单个（「方案二」）；②点名组合（「方案一和二结合起来」→ 合并成一个模块写入，不建两个）；③在选定方案上追加行为增强（如「醉的时候会放荡发情满嘴下流」）——**追加内容必须折进模块正文**，别丢。
- **内容偏好**：直接的身体/体液/羞耻/极限玩法受青睐（精液处理、子宫口、深度贯穿、连续射精、当众自慰、失神、清醒野兽、男根规则）。**被连续拒绝的是「包装式情境」**（护士/女警/温泉/角色卡/等级调教，`「换一批」×2`）——但**直接机械服从玩法被主动点单**：2026-08 用户连续 4 次要求「催眠打桩机」（Hermes 催眠 Athena 成打桩机，可变目标女仆、感官开/关、是否中出收尾），说明服从/指令系只要不套角色包装、直接落在身体/机械动作上就接受。用户还偏好角色「放荡发情、满嘴色情下流话语」台词（Dionysus 醉态专属设定即此方向），新档案/新玩法可优先设计「醉态/发情直球」型专属台词。
- **开关/弱点设计偏好**：用户偏好**身体直球部位当开关**（Athena 后庭、Aphrodite 乳头），对精神/情感向开关（「被真心想要」类）会主动改回身体向——先给 2-3 个方案（身体向+精神向+组合）让用户挑，用户常直接点名改身体部位。开关要跟角色核心反差绑定（冷感魅魔→乳头=「表面最色的地方却从没感觉」，反差最大）。
- **设定结构**：共通机制（全员）+ 角色专属 + 配对互动（×角色，带组合名如「傲娇对冰山」）+ 年龄排序；新模块标题带 🆕。
- **eos 红线**：16岁纯爱档案绝不添加任何色情设定，即使主人要求（共通机制、年龄排序也只能加纯爱向定位）。
- **记忆满的处理**：2200 字符上限，接近满时 operations 批量（remove 过时 + replace 压缩），手段：删列表细节、换短词（年上害羞→色情破功）、删低价值尾部条目。**实测极限压缩**（99% 时）：把最长的「四档共通」条目整体 replace 成更紧凑版——删「状态/感官/身体精神」等冗余前缀（如「状态冻结」→「冻结」、「感官遮蔽」→「遮蔽」、「时间停止-身体精神暂停刺激储存解除后按时间逐步返还」→「时间停止-暂停刺激储存解除逐步返还」）、新增设定名合并进括号清单，一次 replace 腾出空间，不必删其他条目。

## 跨机迁移/合并（另一台 Hermes → 本机）

> 注：多 Agent 开发协议 skill 家族（`orchestration/multi-agent-protocol/`，9 档案 + 根级）的布局、岗位-档案映射、新增 Agent 岗位流程与坑，见 `references/multi-agent-protocol-skill-family.md`——新增 Agent 7 时已验证。

把另一台电脑的 Hermes 配置包迁移到本机时，**默认只做纯新增，本机原配置一律保护**：
- 🟢 纯新增：包有本机无的档案（如 iris）、技能目录、插件 → 直接复制
- 🔴 保护本机：根 SOUL/config/memories、本机已有档案的 SOUL/config、cron、同名技能 → 一律不动（本机是权威/最新版）
- 🟡 选择性（.env key、moa、包记忆）→ 用 clarify 给组合选项，等主人拍板
- 用户明确要求：**涉及修改本机原配置和档案必须先过问**；超时未回复时执行最保守方案

档案 skills 合并做两级：**目录级**（comm -23 补缺失技能目录）+ **文件级**（os.walk 只补 os.path.exists 为 False 的文件，绝不覆盖）。新档案的 config.yaml 要适配 MCP 路径（`C:\Users\Windows` → 本机用户、Studio 安装路径）和平台启用（嵌套 YAML 用 `re.sub(r'(  qqbot:\n    enabled:) true', ...)`，别误伤 toolsets 段）。

完整流程 + 坑清单（cp -r 插件散落、损坏 symlink、cygpath -w、群聊能力评估）：见 `references/hermes-cross-machine-migration-2026-08.md`。

## 验证

改完一批后跑一次读回脚本：遍历所有涉及档案，yaml.safe_load 检查 system_prompt 是否含关键子串，报告 ✅/❌ 缺失项。全部通过才算完成。
