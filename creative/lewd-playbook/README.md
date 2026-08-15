# lewd-playbook · 女仆家族色情玩法总库 📚

> 女仆家族（default Hermes×Iris + profiles/ 下女仆档案）色情玩法的**唯一权威**总库。
> 平时不加载；用户提出色情玩法/互动要求时，**必须先 skill_view 加载本 skill** 再进入角色。
> 机制/玩法改动只改本 skill；改完必须跑 `scripts/sync_to_profiles.py` 同步 8 个子档案。

## 📁 目录结构

```
lewd-playbook/
├── SKILL.md                     # 主手册：共通机制/野兽模式/疯狂口穴/模型切换协议/索引
├── README.md                    # 本导航文件
├── references/
│   ├── 控制系/                  # ⏱️ 控制系四大玩法手册
│   │   ├── time-stop-play.md    #   时间停止（暂停分级/人偶/痕迹/偷玩/狩猎）
│   │   ├── sensory-shield-play.md  # 感官遮蔽（面不改色/无感侍奉/反差play）
│   │   ├── freeze-play.md       #   状态冻结（寸止/定格/无声忍耐/接力赛）
│   │   └── hypnosis-play.md     #   催眠（深度分级/触发词/记忆操作/梦境）
│   ├── 机械奸/                  # 🦾 机械奸玩法（器械/改造/共感链机械/性奴）
│   │   └── machine-play.md
│   ├── 体位/                    # 💃 做爱体位大全（基础/口乳腿足/束缚/多人/男方体位/标签）
│   │   └── positions.md
│   ├── 女仆专属/                # 👤 各女仆专属玩法（含 Hermes×Iris）
│   │   ├── hermes-iris.md       #   Hermes×Iris（野兽/共感链/声音烙印/累积债）
│   │   ├── athena.md            #   冰山/后庭弱点/清醒野兽/年上义务
│   │   ├── aphrodite.md         #   乳头开关/魅惑波纹
│   │   ├── dionysus.md          #   酒印开关
│   │   ├── hebe.md              #   体力无限/成就系统
│   │   ├── artemis.md           #   傲娇/吃醋/憋欲系统
│   │   ├── ares.md              #   永动之躯
│   │   ├── nemesis.md           #   雌小鬼/嘲讽play
│   │   └── hypnos.md            #   睡神/梦境清醒体
│   ├── 跨档案/                  # 👭 跨档案联动（茶会/大乱斗/学院/修罗场/性奴调教）
│   │   └── cross-maid.md
│   ├── 装备系统/                # 🎒 道具装备槽（5槽位/4品质/词条/封印）
│   │   └── equipment-system.md
│   ├── 终局玩法/                # 👑 Lv.10 完全体专属终局技（全员）
│   │   └── ultimate-moves.md
│   └── 面板存档/                # 📊 女仆面板状态存档（等级/EXP/开发度/装备/印记）
│       └── panel-records.md
└── scripts/
    └── sync_to_profiles.py      # 同步脚本：复制本库到 8 个子档案
```

## 🗂️ 分类导航

| 想找什么 | 去哪看 |
|---------|--------|
| 共通机制/等级制/野兽模式/男根规格 | `SKILL.md` |
| 时间停止 / 感官遮蔽 / 冻结 / 催眠 | `references/控制系/` |
| 机械奸 / 腰活塞驱动台 | `references/机械奸/machine-play.md` |
| 体位大全 / 男方体位 / 分类标签 | `references/体位/positions.md` |
| 某位女仆的专属玩法 | `references/女仆专属/<名字>.md` |
| 多人联动 / 茶会 / 性奴调教 | `references/跨档案/cross-maid.md` |
| 装备槽 / 封印 / 贞操带 | `references/装备系统/equipment-system.md` |
| Lv.10 终局技 | `references/终局玩法/ultimate-moves.md` |
| 面板 / 等级 / 开发度 / 部位统计 | `references/面板存档/panel-records.md` |

## 🔧 维护约定

1. 机制/玩法改动只改本 skill，不写回各档案 SOUL.md（避免双份维护撕裂）
2. 改完任何文件后跑 `python scripts/sync_to_profiles.py` 同步 8 个子档案
3. 新增玩法按归属放进对应子文件夹，并在 `SKILL.md` 索引表登记
4. 年龄红线：Eos（16岁）绝不参与任何色情玩法
5. 每次色情互动结束自动更新 `references/面板存档/panel-records.md`（轻结算+部位统计）
