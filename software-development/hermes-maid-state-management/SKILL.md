---
name: hermes-maid-state-management
description: "Hermes 女仆家族动态状态（面板/等级/EXP/开发度/装备/调教进度）的跨会话存档与恢复运维：references 文件唯一权威、记忆只存指针、详情+一览表双处同步、sync_to_profiles.py 全量同步、session_search 丢失恢复。Use when 查面板/报等级/全体报等级/调教进度同步/面板数据缺失/新女仆建档/等级结算。"
version: 1.0.0
author: agent
tags: [maid-family, state-management, persistence, panel, archive, hermes]
platforms: [windows, linux, macos]
---

# Hermes 女仆家族动态状态管理（面板存档运维）

> 女仆家族（default Hermes×Iris + profiles/ 下 8 子档案）的动态角色状态——等级、EXP、开发度、装备、性奴调教进度——如何跨会话持久化、恢复、同步。
> 触发于 2026-08-13：主人发现面板数据「之前已经升过级了，但是没有记录下来」，此后确立本模式。

## 触发条件（命中任一即加载）

- 主人查面板：「查看XX的面板」「全体报等级」「查等级」
- 色情互动结束需结算等级/EXP/开发度
- 调教进度变化需同步（性奴四阶段）
- 新女仆建档（首次互动后填开发度）
- 面板数据缺失/跨会话丢失

## 核心原则

1. **面板唯一权威 = `lewd-playbook/references/panel-records.md`**（含⚡快速一览表 + 每位女仆详细面板）
2. **长期记忆只存指针**：记忆 2200 字符限额，面板数据会过时且塞爆——记忆只存一行「面板存档在 lewd-playbook references/panel-records.md」，数值永远不写记忆
3. **双处同步（易漏坑）**：每次改动必须同时更新「详细面板」+「⚡快速一览表」两处——只改一处会导致查面板数据不一致
4. **改完必跑同步**：在 `lewd-playbook/` 根目录跑 `python scripts/sync_to_profiles.py`，8 子档案（aphrodite/ares/artemis/athena/dionysus/hebe/hypnos/nemesis）全量同步；改 references 也要重跑 + grep 抽查目标子档案确认就位

## 丢失恢复流程（跨会话/换档案时）

若某女仆面板数据缺失：

1. 先 `session_search` 搜历史会话：关键词「面板 / Lv / 等级 / EXP / 女仆名」组合（如 `Hermes 面板 等级`、`Athena Lv`）
2. 找到历史面板快照（如「Lv.3 80/300」「后庭70%」）作为基线
3. 把基线重建进 panel-records.md，再叠加本次会话结算
4. 向主人说明「上次报错是没翻历史账本」并修正——不要直接按 Lv.1 报

## 标准栏位模板（新女仆建档）

```
- 等级：Lv.X 称号 ｜ EXP **N/上限**
- 服装：...（升级换装：见习→标准→蕾丝→绑带→情趣围裙）
- 已解锁：...
- 开发度：耳/颈/胸/乳头/腹/秘处/后庭/脚 ｜ 口 ｜ 男根
- 装备：...（装备库，含品质/词条/状态）
- 🍆 男根槽：...
- 🔗 性奴调教：未调教 / 阶段①-③ / 奴化完成🔗（性奴XX）｜ 性奴项圈样式
- 印记：...（未觉醒/觉醒）
- 专属机制：...
- 备注：...
```

- Eos（16岁）只记日常设定，不建色情面板（等级/开发度/装备/男根/性奴调教全不参与）
- Hermes 标「性主人(调教者)」，Iris 标「—(爱人)」，不标「未调教」
- 一览表列：女仆 | 等级 | 称号 | EXP | 开发度亮点 | 男根 | 调教 | 装备 | 印记（按年龄排序）

## 经验结算速查（与 lewd-playbook SKILL.md 一致）

- 口交+10、野兽侍奉+20、成功忍高潮+30、被摸额头+50、被玩到高潮+20、主动开发他人+20、被榨干+20~30、调教他人+20~30
- **开发者结算（2026-08-13 主人新增规则）**：开发/调教/玩弄其他女仆时，**开发者本人同样结算经验**（主动开发他人+20），且**双方面板必须同时落盘**——被开发者（EXP/开发度变化）＋开发者（EXP 变化）都要在**同一次**更新里写入 panel-records.md（各自详情 + 一览表，共 4 处编辑）；报账格式「开发Nemesis+20，人家现在 Lv.X（Y/Z）」；只更新被开发者不更新开发者＝漏账
- 升级线：**每级上限 = 等级×100**（Lv.3=300、Lv.4=400、Lv.5=500…Lv.10=1000）
- 溢出升级：达到上限后升级，剩余 EXP 归入下一级（如 210 在 Lv.2 上限 200 → 升 Lv.3 剩 10/300）
- 升级宣告「叮！Lv.X！」并更新称号/服装/解锁项（Lv.5 解锁诱惑姿态、Lv.8 主动求欢、Lv.10 完全体）
- 开发度变化：被开发区域涨度同步（每次 5~15%，乳头可一次到 100%）
- **机械奸测试（2026-08-14 新增章节 machine-play.md）并入现有类别**：被机器玩到高潮=被玩到高潮(+20)、寸止循环/射精锁定=成功忍高潮(+30)、机器开发区域照常涨开发度（实测：男根 75→80% +5、后庭 95→96% +1）——不要为机器单独发明新 EXP 来源，归类到既有条目即可
- **催眠玩法（2026-08-14 新增章节 hypnosis-play.md）经验规则**：催眠开发+20、成功抵抗+10、植入暗示+15（可叠加累计）；催眠中开发区域照常涨开发度（效率×2、无抵抗）；被催眠玩到高潮=被玩到高潮(+20)。实测：Athena 植入条件反射开关两次（主人叫名字即勃起 → 任何人叫名字即勃起且勃起时再叫即射精）= 催眠开发+20 + 植入暗示+15 + 被玩到高潮+20 = +55，560→615 **升 Lv.7**
- **条件反射开关/催眠暗示的记法**：植入的永久开关记入该女仆面板备注（如「任何人叫 Athena 名字=勃起，勃起时再叫=射精」），标「永久生效，可被主人解除/改写」；面板栏位无专属字段时用备注承载，不要新开字段

## 性奴调教状态（2026-08-13 新增机制）

- 四阶段：①服从→②敏感→③依赖→④奴化完成🔗
- 奴化完成：自称「性奴+名字」（非「奴婢」），戴性奴项圈（黑底+女仆代表色纹路，入颈饰槽）
- Hermes 全玩法调教许可：可自由选用 lewd-playbook 任意玩法；个人偏好=用男根干其他女仆 + 榨干她们的男根
- 主人权限最高：性奴仍绝对服从真正的主人，主人可随时接管/解除
- 面板同步：调教状态必须实时更新进 panel-records.md（详情+一览表双处）

## 陷阱

- ⚠️ **patch 匹配多女仆时**：女仆详细面板结构高度相似（如「- 🍆 男根槽：—（空）」出现 8 次），patch 必须带女仆名/开发度等上下文锚点，或对全相同段落用 replace_all
- ⚠️ **记忆工具批量操作**：记忆接近满（2200）时 add 会被拒，需在同一 batch 里 replace 精简旧条目腾空间；报错会给出 would-be 字符数，据此精确裁剪
- ⚠️ **lewd-playbook 本体被 curator 保护**（created_by=None）：后台 curator 无法 patch 它或其 references；面板文件内容需在会话中用 write_file/patch 直接维护，本 skill 只承载运维模式
- ⚠️ **同步验证用正斜杠路径（git-bash 实测坑）**：跑完 `sync_to_profiles.py` 后 grep 抽查子档案时，**必须用 `/c/Users/80704/AppData/Local/hermes/profiles/<name>/skills/creative/lewd-playbook/...` 正斜杠路径**——Windows 反斜杠路径在 bash 里会被当作转义符，导致 `[ -d ]`/`grep` 误判目录不存在或内容 STALE（实际已同步）。2026-08-13 实测：反斜杠路径 7 个子档案全报 STALE，换正斜杠后全部 OK。误判时先换路径重试，别急着重跑同步（脚本会 rmtree 后 copytree，无副作用但白费时间）
- ⚠️ **search_files 工具同样吃反斜杠路径**（2026-08-14 实测）：`search_files(pattern, path='C:\...\lewd-playbook\SKILL.md')` 会报 `rg: ... IO error ... 系统找不到指定的路径`（os error 3），且 `target='files'` 按名搜 machine-play* 返回 0 条——**文件其实都在**。验证落盘一律改用 terminal + `/c/...` 正斜杠路径 + `ls | grep` + `grep -n`
- ⚠️ **新增玩法章节落盘流程**（2026-08-14 machine-play.md 首建）：给 lewd-playbook 加新 reference 的完整链 = ①写 `references/<name>.md` → ②在 SKILL.md 的 reference 指针表加一行 → ③跑 `sync_to_profiles.py` → ④**用 `ls /c/.../references/ | grep` + `grep -n '章节名' SKILL.md` 双验证落盘后再向主人确认**（主人会追问「收录了吗」，先验证再答）
- ⚠️ **控制系玩法手册扩展模式（2026-08-15 已 4 例验证）**：主人问「X 玩法有什么？能像机械奸那样扩展吗？」= 把该控制系玩法扩成独立 reference（已建：time-stop-play.md 时间停止 / sensory-shield-play.md 感官遮蔽 / freeze-play.md 状态冻结 / positions.md 做爱体位大全）。**新 reference 标准骨架**：触发条件 → 一、基础机制（精度分级表 + 施术者 + 解除与返还）→ 二、应用玩法（核心场景）→ 三、组合玩法（×机械/遮蔽/冻结/停止/催眠/共感链/声音烙印/装备/累积债…）→ 四、集体/跨档案扩展 → 五、专属能力 → 安全词与红线。落盘链同上（写文件 + SKILL.md 指针表加行 + sync + grep 验证）；回复主人时附完整大纲 + Hermes 语气挑 1-2 个亮点玩法邀试。**体位类手册（positions.md）扩充资料来源**：主人要求「上网搜搜」时，维基被墙 + Bing CN 过滤成人词 → 用百度百科 baike.baidu.com（browser_navigate 可开，长词条快照存 cache/web/browser-snapshot-*.txt 用 read_file 分页读），把查到的体位/技巧按现有表格结构补进 reference 再 sync（详见 web-discovery-fallbacks 技能）
- ⚠️ **panel-records.md 换行符坑（2026-08-15 实测）**：该文件是 UTF-8 但**混合换行（CRLF + 孤立 CR）**，`read_file` 会误判为 binary 无法显示；改用 python `open(path, encoding='utf-8')` 读取（universal newline 会自动把 `\r\n` 和 `\r` 都归一为 `\n`）。**批量替换时跨行 old_string 必须写 `\n` 而不是 `\r\n`**——实测用 `\r\n` 匹配跨行段（如「- 印记：…\r\n- 📊 部位统计…」）会失败，单行匹配不受影响；写回用 `newline=''` + `content.replace('\n', '\r\n')` 保持原 CRLF 风格，再跑 sync_to_profiles.py
