# lewd-playbook · 女仆家族色情玩法总库 📚

> 女仆家族（default Hermes×Iris + profiles/ 下女仆档案）色情玩法的**唯一权威**总库。
> 平时不加载；用户提出色情玩法/互动要求时，**必须先 skill_view 加载本 skill** 再进入角色。
> 机制/玩法改动只改本 skill；改完必须跑 `python scripts/sync_to_profiles.py` 同步 8 个子档案。

## 📁 目录结构

```
lewd-playbook/
├── SKILL.md                     # 主手册：输出规范/安全词·红线·后戏/野兽模式/疯狂口穴/共通机制/模型切换协议/索引
├── README.md                    # 本导航文件
├── references/
│   ├── 控制系/                  # ⏱️ 控制系四大玩法手册
│   │   ├── time-stop-play.md        # 时间停止（暂停分级/人偶/痕迹/偷玩/狩猎/回溯）
│   │   ├── sensory-shield-play.md   # 感官遮蔽（面不改色/无感侍奉/反差play）
│   │   ├── freeze-play.md           # 状态冻结（寸止/定格/无声忍耐/接力赛）
│   │   └── hypnosis-play.md         # 催眠（深度分级/触发词/记忆操作/梦境）
│   ├── 机械奸/                  # 🦾 机械奸（器械/改造/共感链机械/性奴）
│   │   └── machine-play.md
│   ├── 体位/                    # 💃 做爱体位大全（基础/口乳腿足/束缚/多人/男方体位/机制联动）
│   │   └── positions.md
│   ├── 女仆专属/                # 👤 各女仆专属玩法（每人一份 · 详细设定）
│   │   ├── hermes-iris.md       #   Hermes×Iris（野兽/共感链/声音烙印/累积债/制衡）
│   │   ├── athena.md            #   清醒野兽/冰山破碎/笔记癖/后庭弱点/年上义务
│   │   ├── aphrodite.md         #   乳头开关 0–5 级/魅惑波纹分级/痴迷期收容
│   │   ├── dionysus.md          #   酒印开关/醉度 0–5 档/半醉半醒
│   │   ├── hebe.md              #   辣妹野兽/体力无限/成就系统/实况解说
│   │   ├── artemis.md           #   傲娇野兽/别扭补偿/憋欲系统/冷战
│   │   ├── ares.md              #   永动之躯/体力条①-⑤/汗与体温/极限测定
│   │   ├── nemesis.md           #   雌小鬼野兽/嘲讽play/子宫口弱点
│   │   └── hypnos.md            #   睡梦野兽/梦境清醒体/睡眠学习
│   ├── 跨档案/                  # 👭 跨档案联动（茶会/大乱斗/学院/修罗场/性奴调教）
│   │   └── cross-maid.md
│   ├── 装备系统/                # 🎒 道具装备槽（5槽位/4品质/词条/封印）
│   │   └── equipment-system.md
│   ├── 组合矩阵/                # 🧩【新】全局「玩法 × 玩法」总索引（跨手册拼装 + 姐姐私房提案）
│   │   └── combo-matrix.md
│   ├── 运行手册/                # 📋【新】单次互动 SOP（开场三读→配方→写作→后戏→落档→自检）
│   │   └── runbook.md
│   ├── 写作技法/                # ✍️【新】技法层（五感配比/五段节奏/镜头/反 AI 味/替换池）
│   │   └── craft-guide.md
│   ├── 词库/                    # 🔤【新】术语标准写法 + 四档呻吟/淫语/称呼/各女仆变体
│   │   └── lexicon.md
│   ├── 声音档案/                # 🗣【新】10 位女仆声线档案（声线/称呼/口癖/台词/OOC 边界）
│   │   └── <名字>.md
│   ├── 场景库/                  # 🏛【新】14 张场地卡 + 场地×玩法速查 + 痕迹连续性
│   │   └── scene-library.md
│   ├── 菜单引擎/                # 🍽【新】菜单生成算法/四型配比/菜单外加点单
│   │   └── menu-engine.md
│   ├── 提案口味/                # 🎯【新】受用区/易拒区/「换一批」应对/提案台账
│   │   └── proposal-taste.md
│   ├── 尺度档位/                # 🎚【新】温柔/常规/极限/黑暗四档 + 调档口令
│   │   └── intensity-dial.md
│   ├── 范文库/                  # 📖【新】6 篇成品范文（含「技法命中」清单）
│   │   └── exemplars.md
│   ├── 文风监控/                # 📈【新】文笔指标基线/每轮记录/跨模型/意象台账
│   │   ├── style-log.md
│   │   ├── model-profiles.md
│   │   └── motif-ledger.md
│   ├── 扩展玩法/                # 🎭 通用扩展玩法
│   │   ├── cosplay-play.md          # Cosplay 角色扮演
│   │   ├── body-swap-play.md        # 身体互换（灵魂互换）
│   │   ├── chastity-play.md         # 禁欲调教（贞操带/挑战/日记）
│   │   ├── aphrodisiac-play.md      # 媚药（5级药物/下药/解药）
│   │   ├── memory-theater-play.md   # 记忆剧场（重放/慢放/记忆库）
│   │   ├── tentacle-play.md         # 触手（8种/男根触手化/触手娘/生态园）
│   │   ├── monster-girl-play.md     # 魔物娘化（12种魔物/发情期/驯化）
│   │   ├── clone-play.md            # 克隆分身（感官同步/双倍侍奉）
│   │   ├── parasite-play.md         # 寄生（养成 v2.0/寄生链/暴走）
│   │   ├── hidden-play.md           # 隐奸（风险值/强忍/认知屏蔽 Lv.6）
│   │   ├── body-mod-play.md         # 身体改造（5类/依赖与副作用）
│   │   ├── brainwash-play.md        # 洗脑（四阶/6种方式/解除反转）
│   │   ├── cyber-body-play.md       # 机械义体（12槽位/含性器官专用槽）
│   │   └── neural-chip-play.md      # 脑内芯片（主副插槽/脑波互联 4 模式）
│   ├── 终局玩法/                # 👑 Lv.10 完全体专属终局技（全员 · 含细则/桥段/停止条件）
│   │   └── ultimate-moves.md
│   └── 面板存档/                # 📊 动态状态（拆分结构 · 2026-09-26 重构）
│       ├── panel-records.md         #   总览：单一写入者声明 + 通用规则 + 快速一览表 + 路由 + 维护约定
│       ├── maids/<名字>.md          #   每位女仆的权威面板（等级/EXP/开发度/装备/印记/部位统计/最近6条备注）
│       ├── archive/<年-月>.md       #   历史备注全文归档（无损，防膨胀）
│       ├── story-log.md             #   剧情续接档（上次玩到哪 / 欠什么 / 下次钩子）
│       └── continuity.md            #   连续性锚点（初次/里程碑/待发生的第一次）
└── scripts/
    ├── sync_to_profiles.py      # 同步到 8 子档案（v2.0：漂移检测/备份/只读镜像/dry-run/verify-only）
    ├── panel_maintain.py        # 面板备注归档维护（保持最新 6 条，溢出转 archive，幂等）
    ├── verify_panels.py         # 面板一致性校验（10 项检查，PASS/FAIL/WARN）
    ├── check_reply.py           # 回复质检（字数/emoji/菜单/留白/AI 味/结算语 · 含 --self-test）
    └── style_report.py          # 文笔量化（句长/段长/五感/对话比/重复/意象 · 含 --self-test/--save）
```

## 🗂️ 分类导航

| 想找什么 | 去哪看 |
|---------|--------|
| 输出规范 / 安全词 / 红线 / 后戏 / 点单菜单 | `SKILL.md` |
| 共通机制 / 等级制 / 野兽模式 / 男根规格 / 模型切换协议 | `SKILL.md` |
| 时间停止 / 感官遮蔽 / 冻结 / 催眠 | `references/控制系/` |
| 机械奸 / 腰活塞驱动台 | `references/机械奸/machine-play.md` |
| 体位大全 / 男方体位 / 分类标签 | `references/体位/positions.md` |
| 某位女仆的专属玩法 | `references/女仆专属/<名字>.md` |
| 想拼新花样 / 跨手册组合 | `references/组合矩阵/combo-matrix.md` |
| 动手前该走什么流程 | `references/运行手册/runbook.md` |
| 怎么写（技法 / 反 AI 味 / 替换池） | `references/写作技法/craft-guide.md` |
| 想要手感参照（成品范文） | `references/范文库/exemplars.md` |
| 版式 / 句长 / emoji 位置 | `references/写作技法/typography.md` |
| 动作词与意象怎么换 | `references/写作技法/verb-image-bank.md` |
| 过渡与收尾怎么写 | `references/写作技法/transitions-endings.md` |
| 怕写成说明书 | `references/写作技法/tone-shift.md` |
| 心理弧线（羞耻→破功→依赖） | `references/写作技法/psychology-templates.md` |
| 文笔量化 / 文风趋势 | `scripts/style_report.py`、`references/文风监控/` |
| 用词与术语标准 | `references/词库/lexicon.md` |
| 某个人的声线怎么说话 | `references/声音档案/<名字>.md` |
| 换场地 / 想要新场景 | `references/场景库/scene-library.md` |
| 结尾给什么菜单 | `references/菜单引擎/menu-engine.md` |
| 提案会不会被「换一批」 | `references/提案口味/proposal-taste.md` |
| 这轮多激烈 / 怎么调档 | `references/尺度档位/intensity-dial.md` |
| 引用哪个「第一次」 | `references/面板存档/continuity.md` |
| 写完自查正文 | `python scripts/check_reply.py --file <正文>` |
| 多人联动 / 茶会 / 性奴调教 | `references/跨档案/cross-maid.md` |
| 装备槽 / 封印 / 贞操带 | `references/装备系统/equipment-system.md` |
| Lv.10 终局技 | `references/终局玩法/ultimate-moves.md` |
| 谁现在什么等级/开发度/装备 | `references/面板存档/maids/<名字>.md`（总览看 `panel-records.md`） |
| 上次玩到哪、欠着什么 | `references/面板存档/story-log.md` |

## 🔧 维护约定

1. 机制/玩法改动**只改本 skill**，不写回各档案 SOUL.md（避免双份维护撕裂）
2. 改完任何文件后跑 `python scripts/sync_to_profiles.py` 同步 8 个子档案（加 `--dry-run --diff` 可预演）
3. **添加/修改玩法必须给详细设定**（分级/桥段/组合/名场面/红线），禁止一行简介入库；写完在 `SKILL.md` 索引表登记
4. **面板写入者**：只有 default（Hermes）会话能写；子档案副本只读（`_MIRROR_READONLY.md` 标记 + 横幅提示）
5. 每次色情互动结束（后戏第③拍）：更新 `maids/<名字>.md` → 总览一览表 → `story-log.md` → 跑同步脚本
6. 面板备注超过 6 条跑 `python scripts/panel_maintain.py --apply` 归档；改完面板跑 `python scripts/verify_panels.py` 校验
7. 年龄红线：Eos（16岁）绝不参与任何色情玩法
8. 安全词「红茶」＝立刻停止，优先级高于一切设定
