---
name: python-text-rpg
title: Python Text RPG Game Development
description: Design and build text-based RPG games in Python — character classes, leveling systems, maps, battles, shops, and game loops.
category: software-development
---

## When to use

Build a playable text-based RPG from iterative prompts. The user specifies features incrementally (takes the **game designer** persona for feature asks, **code engineer** persona for bug fixes); this skill provides proven patterns for each subsystem so you compose them fast.

**User preferences (this user):**
- All explanations and code output in Chinese
- Bite-sized feature additions, one at a time, iteratively
- When fixing bugs, switch to "代码工程师" persona
- Responds well to structured tables (对比) and bullet-point summaries
- Keep code KISS/DRY, concise, efficient

## Core architecture

```
game_package/
├── __init__.py
├── data.py          # Constants, skill data, items, materials, values
├── character.py     # Main_character class (no internal imports beyond data)
├── items.py         # item/equipment/backpack functions
├── battle.py        # Monster, EliteMonster, battle functions + drops
├── dungeon.py       # DungeonRoom, Dungeon (procedural generation, WASD nav)
├── locations.py     # Location, MainCity, Wilderness, Map
└── main.py          # create_character, main_loop, entry point
```

Alternative: single-file `game.py` is fine for <500 lines, but split into package when exceeding ~800 lines.

## Key design patterns

### 1. Location polymorphism

```python
class Location:
    def __init__(self, name, desc=""):
        self.name = name
        self.desc = desc

class MainCity(Location):
    def rest(self, character): ...
    def shop(self, character): ...

class Wilderness(Location):
    def explore(self, character): ...
```

Then in the main loop, use `isinstance(current_loc, MainCity)` to gate actions.

### 2. Geometric progression for EXP

```python
EXP_BASE = 100
EXP_RATIO = 1.5

def exp_to_next_level(self):
    return round(self.EXP_BASE * (self.EXP_RATIO ** (self.level - 1)))
# => Lv1:100, Lv2:150, Lv3:225, Lv4:337, Lv5:506
```

### 3. Level-up with per-class stat growth

```python
STAT_PER_LEVEL = {
    '战士': (35, 5, 5, 1),   # HP, MP, ATK, SP
    '法师': (15, 40, 1, 7),
}

def gain_exp(self, amount):
    self.exp += amount
    while self.exp >= self.exp_to_next_level():
        self.exp -= self.exp_to_next_level()
        self.level += 1
        hp_g, mp_g, atk_g, sp_g = self.STAT_PER_LEVEL[self.occupation]
        self.hp += hp_g; self.max_hp += hp_g
        self.mp += mp_g; self.max_mp += mp_g
        self.attack += atk_g; self.spell_power += sp_g
```

### 4. Auto-battle (turn-based)

```python
def auto_battle(character, monster):
    while monster.is_alive() and character.hp > 0:
        dmg = max(1, character.attack + random.randint(-2, 3))
        monster.hp -= dmg
        if not monster.is_alive(): break
        mdmg = max(1, monster.attack + random.randint(-2, 2))
        character.hp -= mdmg
    if not monster.is_alive():
        character.gain_exp(monster.exp_reward)
        character.gold += monster.gold_reward
    else:
        character.hp = max(1, character.hp)
```

### 5. Monster scaling

```python
class Monster:
    def __init__(self, player_level):
        scale = 1 + (player_level - 1) * 0.5
        self.hp = int(random.randint(20, 35) * scale)
        self.attack = int(random.randint(4, 8) * scale)
        self.exp_reward = int(round(100*(1.5**(player_level-1)) * random.uniform(0.15, 0.25)))
        self.gold_reward = player_level * random.randint(2, 5)
```

### 6. Exploration (random events)

```python
def explore(self, character):
    roll = random.random()
    if roll < 0.05:           #  5% 精英怪
    elif roll < 0.65:         # 60% 普通怪
    elif roll < 0.85:         # 20% 无事
    else:                     # 15% 宝箱
```

### 7. Shop system

```python
SHOP_ITEMS = [
    {"name": "生命药水", "price": 20, "effect": ("hp", 50)},
    {"name": "铁剑",     "price": 80, "effect": ("attack", 3)},
]

def use_item(character, item):
    field, val = item["effect"]
    if field == "hp":
        character.hp = min(character.hp + val, character.max_hp)
    elif field == "attack":
        character.attack += val
```

### 8. Stackable backpack (per-category limits)

```python
STACK_MAX = 5      # 消耗品堆叠上限
STACK_MAX_MAT = 10 # 素材堆叠上限

def try_add_item(character, item, source="获得"):
    bp = character.backpack
    # 确定堆叠上限
    if item["cat"] == "素材": limit = STACK_MAX_MAT
    elif item["cat"] == "消耗品": limit = STACK_MAX
    else: limit = 1  # 装备/特殊不堆叠
    # 找已有堆叠
    if limit > 1:
        for stack in bp:
            if stack["item"]["name"] == item["name"] and stack["count"] < limit:
                stack["count"] += 1; return True
    # 不堆叠/堆叠满 → 占新格
    if len(bp) < character.backpack_max:
        bp.append({"item": copy.deepcopy(item), "count": 1}); return True
    # 背包满了 → 交互：丢弃旧物 or 放弃新物
```

### 9. Equipment system (4 slots + class restrictions)

```python
SLOT_NAMES = {"weapon":"武器","offhand":"副手","armor":"防具","accessory":"饰品"}

def equip_item(character, item):
    slot = item["slot"]
    # 职业检查
    if item.get("classes") and character.occupation not in item["classes"]:
        print(f"❌ 无法装备（仅限 {'、'.join(item['classes'])}）"); return False
    # 旧装备卸下，效果取消，放回背包
    old = character.equipment[slot]
    if old:
        apply_effect(character, old["effect"][0], old["effect"][1], add=False)
        character.backpack.append({"item": copy.deepcopy(old), "count": 1})
    # 新装备穿上
    character.equipment[slot] = copy.deepcopy(item)
    apply_effect(character, item["effect"][0], item["effect"][1], add=True)
```

### 10. Interactive battle (choice + escape)

```python
def player_attack_action(character):
    print("│ 0 · 普通攻击     │")
    for i, s in enumerate(avail, 1):
        print(f"│ {i} · {s['name']} ({s['desc']})│")
    print("│ E · 逃跑         │")
    sel = input().strip().upper()
    if sel == "E": return "escape", False
    # ... skill execution ...

def interactive_battle(character, monster):
    while monster.is_alive() and character.hp > 0:
        dmg, _ = player_attack_action(character)
        if dmg == "escape":
            if random.random() < 0.6:  # 60% 逃跑成功
                character.hp //= 2; character.mp //= 2; character.gold //= 2
                # 随机丢失1~3堆叠物品
            else:  # 40% 逃跑失败 → 被免费攻击
                mdmg = max(1, monster.attack + random.randint(-2, 2))
                character.hp -= mdmg
                continue
        monster.hp -= dmg
        if not monster.is_alive(): break
        # 怪物反击
        mdmg = max(1, monster.attack + random.randint(-2, 2))
        mdmg = int(mdmg * character.buff)  # 减伤buff
        character.hp -= mdmg
    # 死亡惩罚
    character.backpack.clear()
    for slot in character.equipment: character.equipment[slot] = None
    character.gold = 0; character.hp = 1; character.mp = 1; character.exp = 0
    character._respawn = True  # 主循环检测此标志强制回城
```

### 11. Dungeon system (5×5 grid, union-find connectivity, fog of war)

```python
class Dungeon:
    SIZE = 5
    def _generate(self):
        # 1. 创建25个房间
        # 2. 随机边 → 并查集保证全连通
        edges = []
        for y in range(SIZE):
            for x in range(SIZE):
                if x < SIZE-1: edges.append(((x,y),(x+1,y)))
                if y < SIZE-1: edges.append(((x,y),(x,y+1)))
        random.shuffle(edges)
        # union-find 只取连通必需的边 (MST)
        for a, b in edges:
            if union(a, b):  # 并查集合并
                rooms[a].conn.append(b); rooms[b].conn.append(a)
        # 3. 额外随机加边 (20%) 增加多样性
        # 4. BFS找最远房间 → 设为出口 (exit)
        # 5. 随机分配房间内容: 55%敌人 30%空 15%宝箱
        # 6. 随机起点（非出口），标记已探索

    def show_map(self):
        # 5×5 网格 + 连接线
        # 已探索: 显示图标 (你/·/👾/🎁/🚪)
        # 未探索: 显示 ?
        # 连接: 有连接且至少一端已探索→" "空格, 否则→"│"
        # 垂直: ├──│──┤=有路 ├─────┤=不通
        # 图例: 空格=有路 │=不通  ┼中竖=有路 ─=不通

    def available_moves(self):
        # 返回 dict: {'w':(nx, ny, '↑'), 'a':(nx, ny, '←'), ...}
        # 输入w/a/s/d, 显示↑↓←→

    def enter_room(self, nx, ny):
        # 标记已探索, 自动触发内容事件
        # 事件: enemy→战斗, treasure→宝箱, exit→显示出口选项
```
### 12. Shop with buy/sell + item values

```python
SHOP_ITEMS = [
    {"name":"生命药水","desc":"恢复50HP","price":20,"value":16,"effect":("hp",50),"cat":"消耗品"},
    {"name":"铁剑","desc":"攻击+3","price":80,"value":64,"effect":("attack",3),"cat":"装备",
     "slot":"weapon","classes":["战士","骑士"]},
]
# 售卖价格 = 买入价的80% (整数)
# 素材价值最低 (2~5金), 消耗品中等, 装备最高

def shop(self, character):
    # mode 1: 购买 → 用try_add_item进背包
    # mode 2: 售卖 → 显示背包物品+售价, 支持堆叠售卖
```

### 13. Main loop with dynamic menus + death respawn

```python
LOCATION_ACTIONS = {
    MainCity: [("④","休息","补满HP/MP"),("⑤","锻炼","+10经验"),("⑥","商店","购买/售卖")],
    Wilderness: [("④","探索","地下城")],
}
while True:
    # ── 死亡回城（先于菜单显示）──
    if getattr(character, '_respawn', False):
        character._respawn = False
        current_loc = game_map.locations["主城"]

    print(f"📍 {current_loc.name}")
    print("│ ① 角色状态 ② 地图 ③ 移动 │")
    for k,n,d in LOCATION_ACTIONS.get(type(current_loc), []):
        print(f"│ {k} {n}（{d}）│")
    print("│ ⑦ 背包  ⑧ 退出 │")

    cmd = input().strip()
    # 通用指令 (①/②/③/⑦/⑧) 独立处理
    if cmd in ("①","1"): print(character)
    elif cmd in ("②","2"): ...
    elif cmd in ("③","3"): ...
    elif cmd in ("⑦","7"): backpack_menu(character)
    elif cmd in ("⑧","8"): break
    # 地点专属操作（不阻挡通用指令的 else）
    elif isinstance(current_loc, MainCity):
        if cmd in ("④","4"): current_loc.rest(character)
        elif cmd in ("⑤","5"): current_loc.exercise(character)
        elif cmd in ("⑥","6"): current_loc.shop(character)
```

### 14. Skill system (per-class, MP, level gates)

```python
SKILL_DATA = {
    '战士': [
        {"name":"猛击","lv":1,"mp":0,"desc":"1.5倍伤害","type":"dmg","mult":1.5},
        {"name":"铁壁","lv":5,"mp":10,"desc":"本回合减伤50%","type":"buff","def_mult":0.5},
        {"name":"破军","lv":10,"mp":20,"desc":"2.8倍毁灭打击","type":"dmg","mult":2.8},
    ],
    '法师': [
        {"name":"火球术","lv":1,"mp":15,"desc":"1.8倍法伤","type":"dmg","mult":1.8,"use_sp":True},
        {"name":"法力涌动","lv":5,"mp":0,"desc":"恢复30%MP","type":"re_mp","pct":0.3},
        {"name":"陨石术","lv":10,"mp":35,"desc":"3.5倍法伤","type":"dmg","mult":3.5,"use_sp":True},
    ],
    # ... 牧师/射手/骑士类似
}
# Skill types: dmg(倍率), multi(多段), buff(减伤), re_mp(回蓝), re_hp(回血)
# Player chooses skill during battle, MP cost checked before execution
```

## Verification pattern

Write a standalone script under `C:\Users\Windows\AppData\Local\Temp\hermes-verify-*.py` that:

1. Imports the code via `exec(open(...).read().split("if __name__")[0])`
2. Tests each subsystem independently (monster gen, battle outcome, gold reward, level-up stats)
3. Asserts expected values with clear error messages
4. Cleans up the temp file with `rm -f`

## Pitfalls

- **input() on import**: Use `if __name__ == "__main__":` guard. For testing, `exec(...split("if __name__")[0])` skips the main loop.
- **Geometric exp precision**: Use `round()` not `int()` — `int(100*1.5**3)` = `int(337.5)` = 337, but the clean sequence uses `round(337.5)` = 338.
- **Monster gold scaling**: Keep gold proportional to level. Reduced to `player_level * randint(1,2)` after adding sell system.
- **Player death**: Set `character._respawn = True` and check it AT THE TOP of the main loop (before printing the menu) to avoid showing the wrong location. The flag check must be a standalone `if` block, NOT part of the `elif isinstance(...)` chain, or else universal commands (① status, ② map) get intercepted as "无效指令" after respawn.
- **Ref extraction**: When `browser_type` says "Unknown ref", the DOM changed. Get a fresh `browser_snapshot` or `browser_vision(annotate=True)` to find the new ref IDs.
- **Dungeon connectivity**: Use union-find (MST) to guarantee all 25 rooms are reachable. Just adding random edges will leave isolated rooms. Add extra edges AFTER the MST for variety.
- **Dungeon death**: After death inside the dungeon, `interactive_battle` returns "death" — the `Wilderness.explore()` method must immediately `return` to prevent the dungeon loop from continuing.
- **Equipment stat reversal**: When unequipping, subtract the effect AND clamp `character.hp = min(character.hp, character.max_hp)` so max_hp reduction doesn't leave hp above max.
- **Per-category stacking**: Don't hardcode `STACK_MAX` in `try_add_item`. Use separate constants (`STACK_MAX`=5 for consumables, `STACK_MAX_MAT`=10 for materials) and dispatch by `item["cat"]`.
- **Feishu login flow**: The login popup renders inside an iframe/portal that browser_snapshot can't see. Use `browser_vision(annotate=True)` to locate elements by position, or inject JS into the iframe directly.
- **Dungeon WASD navigation menu offset**: When adding non-move options before movement (status `i`, backpack `b`, map `m`), movement digit parsing must offset: `n = int(cmd) - prefix_count`. Otherwise player input "3" indexes `moves[2]` when only 1 move exists.
- **Module refactoring (single file → package)**: Create `__init__.py`, move imports to relative (`from .module import ...`). Ensure `data.py` has no internal imports to avoid circular deps. `character.py` only imports from `data.py`.
- **Random dungeon start**: Use `random.choice([p for p in rooms if p != exit_pos])` instead of hardcoded `(0,0)`. All generation logic stays the same.
- **Exit room persistence**: NEVER set `room.content = "empty"` on the exit room. Instead, let players choose 'r' in exit room to access a 3-option prompt (next floor / return / cancel), and move away freely. Only 'r' works in exit room; in other rooms show "❌ 只有出口房间才能返回地面".
- **Map connection display**: Show `" "` (path exists) if rooms ARE connected AND at least one is explored. Show `"│"` (blocked) if no connection. Never introduce ambiguous symbols like `·`. The legend should say `空格=有路 │=不通`.
- **Skill arrow labels**: `available_moves()` should return dict with WASD keys and 3-tuple values: `moves['d'] = (nx, ny, '→')`. Display arrows to player, accept WASD as input.
