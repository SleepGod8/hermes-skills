---
name: python-rpg-systems
description: Python RPG game system design — character classes, geometric progression leveling, map/location architecture, interactive combat, skill systems, economy, backpack, and game loops
---

# python-rpg-systems

## When to load
- User is building an RPG game system in Python
- User needs level-up mechanics, EXP formulas, or map systems
- User asks about class-based character design with occupation-specific stats
- User needs battle systems, skills, shops, inventory, or interactive CLI game loops
- **Trigger phrases**: "以游戏设计师的身份", "以游戏代码工程师的身份", "添加XX系统", "优化操作页面", "修一下游戏的bug"
- **Project root**: The game lives at `D:/PythonProject/Land of Heroes/`
- **Entry point**: `python run.py` (calls `land_of_heroes.main.main_loop()`)
- **Package structure**: `land_of_heroes/` directory with submodules (see Refactoring section)
- **Game title**: Use English + Chinese format: `━━━ ⚔️  Name · 中文名 ━━━` (e.g., `Land of Heroes · 勇者大陆`)

## Character class pattern

```python
class Character:
    STAT_PER_LEVEL = {
        '战士': (35, 5, 5, 1),   # hp_g, mp_g, atk_g, sp_g
        '法师': (15, 40, 1, 7),
        '牧师': (20, 30, 2, 6),
        '射手': (25, 15, 3, 1),
        '骑士': (40, 10, 4, 2),
    }
    INIT_STATS = {
        '战士': (150, 30, 25, 3),
        '法师': (80, 200, 5, 35),
        '牧师': (100, 150, 8, 30),
        '射手': (120, 80, 15, 5),
        '骑士': (200, 50, 18, 8),
    }

    def __init__(self, name, occupation):
        st = self.INIT_STATS[occupation]
        self.hp, self.mp, self.attack, self.spell_power = st
        self.max_hp, self.max_mp = self.hp, self.mp
        self.level = 1; self.exp = 0; self.gold = 0
        self.buff = 1.0  # damage reduction multiplier (for skills)
        self.backpack = []; self.backpack_max = 10
```

**Key design decisions:**
- Store both `hp` (current) and `max_hp` (ceiling for rest)
- `INIT_STATS` dict + `STAT_PER_LEVEL` dict per occupation — cleaner than if/elif chains
- Occupation as dict key — enables simple lookup
- `buff` field tracks per-turn damage reduction (for defensive skills)
- `backpack` is a list of item dicts; `backpack_max` controls capacity

## Level system — geometric progression EXP

```python
EXP_BASE = 100; EXP_RATIO = 1.5

def exp_to_next_level(self):
    return round(EXP_BASE * (EXP_RATIO ** (self.level - 1)))
    # Lv1→2: 100, Lv2→3: 150, Lv3→4: 225, Lv4→5: 338, Lv5→6: 506
```

**Use `round()` not `int()`** — `int(100 * 1.5^3)` truncates to 337 instead of 338.

### Gain EXP with overflow

```python
def gain_exp(self, amount):
    self.exp += amount
    while self.exp >= self.exp_to_next_level():
        self.exp -= self.exp_to_next_level()
        self.level += 1
        hp_g, mp_g, atk_g, sp_g = self.STAT_PER_LEVEL[self.occupation]
        self.hp += hp_g; self.mp += mp_g
        self.max_hp += hp_g; self.max_mp += mp_g
        self.attack += atk_g; self.spell_power += sp_g
```

**Always update both `hp` and `max_hp`** — otherwise resting restores to a stale cap.

## Map / Location architecture

```python
class Location:
    def __init__(self, name, desc=""):
        self.name = name; self.desc = desc

class MainCity(Location):
    def rest(self, character):
        character.hp = character.max_hp; character.mp = character.max_mp

    def exercise(self, character):
        character.gain_exp(10)  # small fixed training gain

    def shop(self, character):
        # see Economy section below

class Wilderness(Location):
    def explore(self, character):
        # random events: monster battle (60%), nothing (20%), treasure (15%), elite (5%)
        # see Battle system section

class Map:
    def __init__(self):
        self.locations = {"主城": MainCity(), "野外": Wilderness()}
    def go(self, name):
        return self.locations.get(name)
```

**Use `isinstance()` for location-specific actions in the game loop:**
```python
if isinstance(current_loc, MainCity):
    current_loc.rest(character)
```

## Equipment system

### 4 equipment slots

```python
SLOT_NAMES = {"weapon":"武器","offhand":"副手","armor":"防具","accessory":"饰品"}
character.equipment = {"weapon":None,"offhand":None,"armor":None,"accessory":None}
```

**Key rules:**
- Each slot holds exactly one item
- Equipping a new item when slot is occupied **returns old item to backpack**
- Equipment is **never consumed** — only moved between slots and backpack

### Class restrictions

```python
{"name":"铁剑","cat":"装备","slot":"weapon","classes":["战士","骑士"]}
{"name":"护心镜","cat":"装备","slot":"accessory","classes":None}  # all classes
```

- `classes: None` or omitted → all classes can equip
- `classes: ["A","B"]` → only listed classes
- On equip failure: print `❌ {职业} 无法装备 {物品}（仅限 {允许的职业}）`

### equip_item pattern

```python
def equip_item(character, item):
    slot = item["slot"]
    if item.get("classes") and character.occupation not in item["classes"]:
        return False  # class restriction
    old = character.equipment[slot]
    if old:
        apply_effect(character, old["effect"][0], old["effect"][1], add=False)
        character.backpack.append({"item": copy.deepcopy(old), "count": 1})
    character.equipment[slot] = copy.deepcopy(item)
    apply_effect(character, item["effect"][0], item["effect"][1], add=True)
    return True
```

### apply_effect — toggleable stat modifier

```python
def apply_effect(character, field, val, add=True):
    s = 1 if add else -1
    if field == "attack": character.attack += val * s
    elif field == "spell_power": character.spell_power += val * s
    elif field == "max_hp":
        character.max_hp += val * s
        if add: character.hp += val
        else: character.hp = min(character.hp, character.max_hp)
```

The same function handles **equip** (add=True) and **unequip** (add=False) via the `s` multiplier.

### Status display

```
━━ 装备 ━━
    武器: 铁剑 (攻击+3)
    副手: （空）
    防具: 锁甲 (HP+50)
    饰品: 护心镜 (HP+30)


## Backpack / Inventory system

### Save data format

```python
SAVES_FILE = os.path.join(project_dir, "saves.json")

def make_save_data(character):
    return {
        "id": f"{character.name}_{character.occupation}",
        "name": character.name, "occupation": character.occupation,
        "level": character.level, "exp": character.exp,
        "hp": character.hp, "max_hp": character.max_hp,
        "mp": character.mp, "max_mp": character.max_mp,
        "attack": character.attack, "spell_power": character.spell_power,
        "gold": character.gold, "backpack_max": character.backpack_max,
        "backpack": [{"name":s["item"]["name"], "count":s["count"], ...} for s in character.backpack],
        "equipment": {key: eq_data if eq else None for key, eq in character.equipment.items()},
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
```

### Overwrite detection

Same-character saves overwrite by matching `id`:
```python
saves = load_saves()
for i, s in enumerate(saves):
    if s["id"] == save_data["id"]:
        saves[i] = save_data  # overwrite
        break
else:
    saves.append(save_data)  # new save
save_saves(saves)
```

### Restore from save

```python
def restore_character(save_data):
    c = Main_character(save_data["name"], save_data["occupation"])
    c.level = save_data["level"]; c.exp = save_data["exp"]
    c.hp = save_data["hp"]; c.max_hp = save_data["max_hp"]
    # ... restore all stats, backpack, equipment ...
    c.backpack = [{"item": item_dict, "count": bd["count"]} for bd in save_data["backpack"]]
    for key in c.equipment:
        c.equipment[key] = restore_item(save_data["equipment"].get(key))
    return c
```

### Save API pattern (FastAPI)

```python
@app.get("/api/saves")
def get_saves(): return {"saves": load_saves()}

@app.post("/api/save/{sid}")
def save_game(sid: str):
    gs = games.get(sid)
    save_data = make_save_data(gs.character)
    # overwrite logic...
    return {"msg": f"✅ 存档成功！{name} Lv.{level}"}

@app.post("/api/load/{save_id}")
def load_game(save_id: str):
    for s in load_saves():
        if s["id"] == save_id:
            c = restore_character(s)
            gs = GameState(c)
            sid = str(uuid.uuid4())[:8]
            games[sid] = gs
            return {"session_id": sid, "state": gs.to_dict()}
```

### Frontend: save button + character list

```javascript
// Save (main city button)
function saveGame() {
  fetch(`/api/save/${SID}`, {method:'POST'}).then(r=>r.json()).then(d => {
    STATE.messages.push(d.msg); render();
  });
}

// Load (character select screen)
async function loadSaves() {
  const data = await (await fetch('/api/saves')).json();
  // Show cards with name, level, occupation, gold, save time
  el.innerHTML = data.saves.map(s => `
    <div class="save-card">
      <span>${s.name} Lv.${s.level} ${s.occupation} 💰${s.gold}</span>
      <button onclick="loadSave('${s.id}')">读取</button>
      <button onclick="deleteSave('${s.id}')">删除</button>
    </div>
  `).join('');
}

// goHome — return to character select without browser refresh
function goHome() {
  document.getElementById('game-screen').style.display = 'none';
  document.getElementById('create-screen').style.display = 'flex';
  STATE = null; SID = null;
  loadSaves();  // refresh save list
}

### Item values (sell price)

| Category | Value range | Examples |
|----------|------------|---------|
| Materials | 2–5 gold | 破旧布片=2, 魔力核心=5 |
| Consumables | 12–16 gold | 生命药水=16 (80% of 20 buy) |
| Equipment | 35–80 gold | 铁剑=64 (80% of 80) |
| Special | 240 gold | 扩容背包=240 (80% of 300) |

### Shop with buy/sell modes

```
🏪 兵器铺 · 💰120
┌── 操作 ─────────┐
│ 1 · 购买          │
│ 2 · 售卖          │
│ 0 · 离开          │
└─────────────────┘
```

### Sell-all (web frontend)

Add a "全部售卖" button that sells every sellable item at once:

```python
elif act == "sell_all":
    total = 0; names = []
    for s in list(c.backpack):
        val = s["item"].get("value", 0)
        if val > 0:
            total += val * s["count"]
            names.append(f"{s['item']['name']}x{s['count']}")
            c.backpack.remove(s)
    if total > 0:
        c.gold += total
        gs.add_msg(f"💰 全部售卖！获得 {total}金")
    else:
        gs.add_msg("❌ 没有可售卖的物品")
```

### Dynamic backpack pricing (geometric scaling)

Base price: 500 gold. Each purchase increases the price geometrically. The number of previous purchases is inferred from `backpack_max`:

```python
# Server-side buy handler:
purchases = (c.backpack_max - 10) // 5  # starts at 10, +5 per purchase
price = int(500 * (1.5 ** purchases))
```

| Purchases | Price |
|-----------|-------|
| 0 (10 slots) | 500 |
| 1 (15 slots) | 750 |
| 2 (20 slots) | 1,125 |
| 3 (25 slots) | 1,687 |

**Frontend display:** Override the static price from SHOP_ITEMS with the calculated dynamic price:
```javascript
if (it.name === '扩容背包') {
  const purchases = Math.floor((STATE.backpack_max - 10) / 5);
  price = Math.floor(500 * Math.pow(1.5, purchases));
  priceText = `${price}金（已扩容${purchases}次）`;
}
```

### Shop purchases → backpack

Items go into the backpack instead of being used immediately. Use `try_add_item()` which handles full-backpack logic.

### Special instant items

"扩容背包" (backpack expansion) applies instantly via `use_item()`, not into backpack:
```python
if item["name"] == "扩容背包":
    use_item(character, item)  # applies backpack_max +5 directly
else:
    try_add_item(character, item, "购买")  # goes to backpack
```

## Backpack / Inventory system

### Data model
- `character.backpack` — list of item dicts
- `character.backpack_max` — max slots (starts at 10, expandable to 15+)

### Item format
```python
{"name":"生命药水","desc":"恢复50HP","price":20,"effect":("hp",50),"cat":"消耗品"}
{"name":"铁剑","desc":"攻击+3","price":80,"effect":("attack",3),"cat":"装备"}
```

### Item categories
- `"消耗品"` — consumables (potions): use → apply effect → remove from backpack
- `"装备"` — equipment (weapons/armor): equip → apply permanent stat boost → remove from backpack
- `"特殊"` — special items (backpack expansion): apply instantly at purchase time

### Item stacking (per-category limits)

```python
STACK_MAX = 5      # consumables (消耗品)
STACK_MAX_MAT = 10 # materials (素材)
```

**Backpack data model:** `list[{"item": item_dict, "count": int}]`

- **Consumables** — stack up to 5
- **Materials** — stack up to 10
- **Equipment** — no stacking, count always 1
- **Display**: show `xN` when count > 1

### try_add_item with stacking

```python
def try_add_item(character, item, source="获得"):
    bp = character.backpack
    if item["cat"] == "素材": limit = STACK_MAX_MAT
    elif item["cat"] == "消耗品": limit = STACK_MAX
    else: limit = 1
    if limit > 1:
        for stack in bp:
            if stack["item"]["name"] == item["name"] and stack["count"] < limit:
                stack["count"] += 1; return True
    if len(bp) < character.backpack_max:
        bp.append({"item": copy.deepcopy(item), "count": 1}); return True
    # Full backpack → prompt user to discard or abandon
```

**Stack matching by `item["name"]`** — same name = same stack.

### Discard from stack

When `count > 1` and user discards: `丢弃几个？（1~5，输a全丢）`
- `a` → remove entire stack
- Number N → decrement count by N
- Empty/other → treat as discard all

### Backpack menu

```
🎒 背包 [3/10]
┌── 物品 ────────────────────┐
│ 1. [消耗品]生命药水 恢复50HP│
│ 2. [装备]铁剑      攻击+3  │
├────────────────────────────┤
│ U · 使用/装备   D · 丢弃   │
│ 0 · 返回                    │
└────────────────────────────┘
```

**Use `copy.deepcopy()` when adding items to backpack** — otherwise multiple items reference the same mutable dict.

## Enemy scaling — by dungeon floor, not player level

**Changed design:** Monsters scale with dungeon floor level, not player level. This makes re-entering floor 1 easy for high-level players, but rewards only come from deeper floors.

### Monster stats per floor

```python
class Monster:
    def __init__(self, floor_level):
        self.name = random.choice(MONSTER_NAMES)
        scale = 1.0 + (floor_level - 1) * 0.8  # F1:1.0, F2:1.8, F3:2.6...
        self.hp = int(random.randint(20, 35) * scale)
        self.max_hp = self.hp
        self.attack = int(random.randint(4, 8) * scale)
        self.floor_level = floor_level
```

**Scale formula:** `1.0 + (floor - 1) * 0.8` — steeper per-floor growth compared to old player-level scaling.

### Reward function with level-based penalty

Rewards are computed separately from stats, using a multiplier based on player level vs floor level:

```python
def _reward_mult(player_level, floor_level):
    """Higher floors needed for better rewards as you level up"""
    return min(1.0, max(0.1, 1.0 - (player_level - floor_level * 2 - 1) * 0.2))

class Monster:
    def reward_exp(self, player_level):
        base = int(round(100 * (1.5 ** (self.floor_level - 1)) * random.uniform(0.15, 0.25)))
        return int(base * _reward_mult(player_level, self.floor_level))

    def reward_gold(self, player_level):
        base = self.floor_level * random.randint(1, 2)
        return int(base * _reward_mult(player_level, self.floor_level))
```

| Player level | Floor 1 reward | Floor 3 reward | Floor 5 reward |
|-------------|---------------|---------------|---------------|
| 1 | 100% | 100% | 100% |
| 5 | 60% | 100% | 100% |
| 10 | 10% | 60% | 100% |

**Rule of thumb:** You need floor ~player_level/2 for full rewards.

### EliteMonster (15% chance)

```python
class EliteMonster(Monster):
    def __init__(self, floor_level):
        super().__init__(floor_level)
        self.name = f"精英{self.base_name}"
        self.hp = int(random.randint(35, 50) * scale * 1.5)
        self.attack = int(random.randint(6, 12) * scale * 1.3)

    def reward_exp(self, player_level): return int(base * 2.5 * mult)
    def reward_gold(self, player_level): return int(base * 2.5 * mult)  # approx
```

**Track `base_name` separately** — `self.base_name` stores the original monster name before the `"精英"` prefix, enabling material lookup for elite kills (MONSTER_MATERIALS keys use base names only).

### Monster drops / materials

```python
roll = random.random()
if roll < 0.05:       # 5% — rare equipment
    loot = random.choice(TREASURE_LOOT); try_add_item(character, loot, "掉落")
elif roll < 0.75:     # 70% — material
    mat_name = MONSTER_MATERIALS.get(monster.base_name, "未知材料")
    mat_item = {"name":mat_name,"value":MATERIAL_VALUES.get(mat_name,3),
                "effect":("none",0),"cat":"素材"}
    try_add_item(character, mat_item, "掉落")
```

**Add a message for material drops** so the player sees what they got:
```python
gs.add_msg(f"📦 掉落 {mat_name}！")
```

### Monster → material mapping

```python
MONSTER_MATERIALS = {
    "山贼":"破旧布片", "野狼":"锋利的狼牙", "毒蛇":"剧毒蛇鳞",
    "流寇":"掠夺品",   "巨熊":"厚实熊掌",   "哥布林":"哥布林的牙齿",
    "骷髅兵":"骨碎片", "石像鬼":"魔力核心", "暗影豹":"暗影皮毛",
}
MATERIAL_VALUES = {
    "破旧布片":2, "锋利的狼牙":3, "剧毒蛇鳞":4, "掠夺品":3,
    "厚实熊掌":5, "哥布林的牙齿":2, "骨碎片":3, "魔力核心":5, "暗影皮毛":4,
}
```

**Drop rates:** 5% equipment, 70% material, 25% nothing. Materials worth 2–5g.

## Failure penalty system

### Battle escape mechanics

Add `E · 逃跑` option to `player_attack_action()`:

```python
print("│ E · 逃跑         │")
# In the input handler:
if sel == "E":
    return "escape", None  # special signal
```

### Escape resolution in battle loop

```python
if dmg == "escape":
    if random.random() < 0.6:  # 60% success
        character.hp = max(1, character.hp // 2)
        character.mp = max(1, character.mp // 2)
        character.gold = character.gold // 2
        # lose 1-3 random backpack stacks
        if character.backpack:
            n = random.randint(1, min(3, len(character.backpack)))
            random.shuffle(character.backpack)
            character.backpack = character.backpack[n:]
        return "escape"
    else:  # 40% fail → monster free attack
        md = max(1, monster.attack + random.randint(-2, 2))
        character.hp -= md
        continue  # next turn
```

**On success:** HP/MP/gold halved, 1–3 random backpack stacks lost.
**On failure:** monster gets a free attack; player stays in combat.

### Death penalty

When HP reaches 0 in battle:

```python
# Full wipe:
character.backpack.clear()
for slot in character.equipment:
    character.equipment[slot] = None
character.gold = 0
character.hp = 1; character.mp = 1
character.exp = 0
# Recalculate stats (base + level growth only, no equipment):
st = Main_character.INIT_STATS[character.occupation]
hp_g, mp_g, atk_g, sp_g = Main_character.STAT_PER_LEVEL[character.occupation]
lv = character.level
character.max_hp = st[0] + hp_g * (lv - 1)
# ... same for max_mp, attack, spell_power
character._respawn = True  # flag for main loop
```

### Respawn in main loop — placement matters

The `_respawn` flag must be checked **at the TOP of the while loop** (before printing menu), and must be a **standalone `if`** (not an `elif` chained with location-specific actions):

```python
while True:
    # ✅ Check respawn BEFORE rendering location/menu
    if getattr(character, '_respawn', False):
        character._respawn = False
        current_loc = game_map.locations["主城"]
        print(f"🚶 你被送回了{current_loc.name}……")

    print(f"📍 {current_loc.name} —— {current_loc.desc}")
    # ... menu, commands, location-specific actions ...
```

**Two common bugs to avoid:**

1. **Placing respawn check AFTER menu rendering** → menu shows "📍 野外" one more time before updating to "主城", confusing the player.
2. **Using `elif isinstance(...)` instead of standalone `if`** → the respawn branch intercepts the user's next command. Pressing `①` for status gets treated as a MainCity-specific action and prints "❌ 无效指令".

The respawn check and the location-action dispatch must be completely independent `if` blocks:

```python
# ✅ Standalone respawn check
if getattr(character, '_respawn', False):
    character._respawn = False
    current_loc = game_map.locations["主城"]

# ✅ Independent location-action chain
if isinstance(current_loc, MainCity):
    ...
elif isinstance(current_loc, Wilderness):
    ...
```

**Death consequences:** all items/equipment/gold lost, EXP zeroed (level kept), HP/MP set to 1, forced teleport to main city.

## Skill system

### Per-occupation skills with level gates

```python
SKILL_DATA = {
    '战士': [
        {"name":"猛击","lv":1,"mp":0,"desc":"1.5倍伤害","type":"dmg","mult":1.5},
        {"name":"铁壁","lv":5,"mp":10,"desc":"减伤50%","type":"buff","def_mult":0.5},
        {"name":"破军","lv":10,"mp":20,"desc":"2.8倍打击","type":"dmg","mult":2.8},
    ],
    '法师': [
        {"name":"火球术","lv":1,"mp":15,"desc":"1.8倍法伤","type":"dmg","mult":1.8,"use_sp":True},
        {"name":"法力涌动","lv":5,"mp":0,"desc":"恢复30%MP","type":"re_mp","pct":0.3},
        {"name":"陨石术","lv":10,"mp":35,"desc":"3.5倍法伤","type":"dmg","mult":3.5,"use_sp":True},
    ],
    # 牧师: 圣光弹(Lv1) / 治愈术(Lv5) / 惩戒(Lv10)
    # 射手: 精准射击(Lv1) / 连射(Lv5) / 致命一击(Lv10)
    # 骑士: 突刺(Lv1) / 守护(Lv5) / 圣骑冲锋(Lv10)
}
```

### Skill types

| type | Behavior | Fields | Notes |
|------|----------|--------|-------|
| `dmg` | Damage with multiplier | `mult`, optional `use_sp` (use spell_power instead of attack), optional `heal_pct` | |
| `multi` | Multi-hit damage | `mult`, `hits` | Sum all hits into one damage value; show each hit in message |
| `buff` | Damage reduction for N turns | `def_mult`, `turns` | Set `character.buff` and `character.buff_turns`; decrement each turn |
| `re_mp` | Restore MP percentage | `pct` | |
| `re_hp` | Restore HP percentage | `pct` | |

### Multi-turn buff system (`buff_turns`)

For skills like 铁壁 (3-turn 50% damage reduction):

**Skill data:**
```python
{"name":"铁壁","lv":5,"mp":10,"desc":"3回合减伤50%","type":"buff","def_mult":0.5,"turns":3}
```

**On skill use (player_turn / battle.py):**
```python
elif skill["type"] == "buff":
    character.buff = skill["def_mult"]  # e.g., 0.5 for 50% reduction
    character.buff_turns = skill.get("turns", 1)
    print(f"  🛡️  释放【{skill['name']}】，{turns}回合减伤{int((1-buff)*100)}%！")
    return 0, True  # no damage, turn ends
```

**At start of each battle turn (decrement buff):**
```python
character.buff = 1.0  # default: no reduction
bt = getattr(character, 'buff_turns', 0)
if bt > 0:
    character.buff_turns = bt - 1
    if character.buff_turns <= 0:
        character.buff = 1.0  # buff expired
```

**In monster counter-attack (apply buff reduction):**
```python
dmg = max(1, monster.attack + randint(-2,2))
buff = getattr(character, 'buff', 1.0)
dmg = int(dmg * buff)  # e.g., 50% → half damage
bt = getattr(character, 'buff_turns', 0)
suffix = f" 🛡️({bt-1}回合剩)" if buff < 1 else ""
```

### Multi-hit skill type (`multi`)

For skills like 连射 (1.5倍 × 2 hits):

**Skill data:**
```python
{"name":"连射","lv":5,"mp":15,"desc":"1.5倍×2连击","type":"multi","mult":1.5,"hits":2}
```

**Damage calculation (sum all hits):**
```python
elif skill["type"] == "multi":
    hits = skill.get("hits", 2); total = 0; parts = []
    for h in range(hits):
        d = max(1, int(character.attack * skill.get("mult", 1.5)))
        total += d; parts.append(f"第{h+1}击{d}伤")
    dmg = total
    msg = f"⚡ {character.name} 使用 {skill['name']}！{' '.join(parts)} 总计 {dmg} 点伤害"
```

**Important:** The `else` fallback in `player_turn` must NOT catch `multi` type — add an explicit `elif` branch for it before the `else`.

### Web server battle (FastAPI version)

When building a web frontend the terminal `input()` calls must be replaced with event-driven API endpoints. The web server has its own battle logic:

```python
def player_turn(character, monster, skill=None):
    """Returns (msg, is_victory) — no input() calls"""
    if skill:
        cost = skill.get("mp", 0)
        if character.mp < cost:
            return f"❌ MP不足！需要 {cost}MP", False
        character.mp -= cost
        if skill["type"] == "dmg":
            dmg = int(character.attack * skill.get("mult", 1.5))
        elif skill["type"] == "multi":
            hits = skill.get("hits", 2); total = 0; parts = []
            for h in range(hits):
                d = max(1, int(character.attack * skill.get("mult", 1.5)))
                total += d; parts.append(f"第{h+1}击{d}伤")
            dmg = total
            msg = f"⚡ {character.name} 使用 {skill['name']}！{' '.join(parts)} 总计 {dmg} 点伤害"
        elif skill["type"] == "magic":
            dmg = int(character.spell_power * skill.get("mult", 2.0))
        elif skill["type"] == "buff":
            character.buff = skill.get("def_mult", 0.5)
            character.buff_turns = skill.get("turns", 1)
            return f"🛡️ 释放【{skill['name']}】,{buff_turns}回合减伤{pct}%", False  # early return
        else:
            dmg = int(character.attack * skill.get("mult", 1.0))
        if 'msg' not in dir(): msg = f"⚡ 使用 {skill['name']}！造成 {dmg} 点伤害"
    # monster.hp -= dmg, check victory/death, monster counter-attack...
```

### Battle: using consumables triggers monster counter-attack

When the player uses a potion during battle, the enemy should also act:

```python
elif act == "use_item":
    ...
    if item["cat"] == "消耗品":
        use_item(c, item)
        gs.add_msg(f"💚 使用了 {item['name']}")
        # ✅ Monster counter-attacks after item use in battle
        if gs.fighting and gs.enemy and gs.enemy.hp > 0:
            msg2, death = monster_turn(c, gs.enemy)
            gs.add_msg(msg2)
            if death:
                # handle player death...
```

### Frontend: MP-insufficient skills grayed out

In the battle UI, disable skill buttons when player lacks MP:

```javascript
STATE.skills.forEach((sk, i) => {
  const noMP = sk.mp > STATE.mp;
  btns.push({
    text: `⚡ ${sk.name} [${sk.mp}MP]`,
    cls: 'btn' + (noMP ? ' disabled' : ''),
    act: noMP ? '' : 'battle_attack',
    payload: {skill: i},
    tip: `${sk.desc}（${sk.mp}MP）${noMP ? ' MP不足' : ''}`
  });
});

### Combat interaction — player chooses each turn

```
⚔️  你的回合 · MP:30/30
┌── 行动 ─────────┐
│ 0 · 普通攻击     │
│ 1 · 猛击（1.5倍 无消耗）│
│ 2 · 铁壁（减伤50% MP:10）│
└─────────────────┘
```

- Player picks 0 for normal attack, or a number for a skill
- Skills consume MP; if insufficient MP, show error and re-prompt
- `character.buff` resets to 1.0 at start of each turn, then skills set it (e.g., 0.5 for 50% reduction)

### Interactive battle loop

```python
def interactive_battle(character, monster):
    turn = 0
    while monster.is_alive() and character.hp > 0:
        turn += 1
        character.buff = 1.0  # reset damage reduction
        dmg, _ = player_attack_action(character)
        monster.hp -= dmg
        if not monster.is_alive(): break
        # monster counter-attack
        monster_dmg = max(1, monster.attack + randint(-2,2))
        monster_dmg = int(monster_dmg * character.buff)  # apply buff
        character.hp -= monster_dmg
```

## Treasure chest system

15% chance on wilderness exploration:
- EXP: `int(exp_to_next_level() * 0.1)`
- Gold: `level × random(10, 25)`
- 50% chance of additional item from `TREASURE_LOOT` pool:
  - 特效治疗药 (restore 120 HP), 特效魔力药 (restore 120 MP)
  - 玄铁剑 (ATK+8), 星辉法袍 (SP+12), 龙鳞甲 (max HP+60)

## Dungeon system (5×5 grid with fog of war)

### Dungeon generation

```python
class Dungeon:
    SIZE = 5
    def __init__(self, floor=1):
        self.floor = floor
        self.px, self.py = 0, 0  # player position
        self.rooms = {}          # (x,y) → DungeonRoom
        self._generate()
```

**Room data model:**
```python
class DungeonRoom:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.explored = False     # fog of war
        self.content = "empty"    # empty/enemy/treasure/exit
        self.conn = []            # [(nx,ny), ...] connected rooms
```

### Connectivity guarantee (union-find spanning tree)

All 25 rooms must be reachable from (0,0):

```python
edges = [(相邻房间对)...]  # right and down neighbors
random.shuffle(edges)
parent = {p: p for p in self.rooms}
def find(p): ...
def union(a, b): ...
for a, b in edges:
    if union(a, b):  # connect rooms in different sets
        self.rooms[a].conn.append(b)
        self.rooms[b].conn.append(a)
# Random extra edges (20%) for variety
```

### Exit placement — BFS farthest room

```python
dist = {p: 999 for p in self.rooms}; dist[(0,0)] = 0
q = [(0,0)]
while q:
    cur = q.pop(0)
    for nb in self.rooms[cur].conn:
        if dist[nb] > dist[cur] + 1:
            dist[nb] = dist[cur] + 1; q.append(nb)
exit_pos = max(dist, key=lambda p: dist[p])  # farthest from start
```

### Room content assignment

| Content | Probability | Notes |
|---------|-----------|-------|
| `enemy` | 55% | 15% elite, 85% normal; level scales with floor |
| `empty` | 30% | Safe room |
| `treasure` | 15% | EXP + gold + 60% equip drop |

Start room (0,0) is always empty; exit room is pre-assigned.

### Fog of war map display

```
┌─────┬─────┬─────┬─────┬─────┐
│ 你     ·  │  ?  │  ?  │  ?  │
├─────┼──│──┼─────┼─────┼─────┤
│ 👾 │  ?  │  ?  │  ?  │  ?  │
├─────┼─────┼─────┼─────┼─────┤
│  ?  │  ?  │  ?  │  ?  │  ?  │
└─────┴─────┴─────┴─────┴─────┘
```

- **Unvisited rooms** show `?` (fog of war)
- **Horizontal connection**: space ` ` = connected, `│` = blocked
- **Vertical connection**: `│` in the middle of `──│──` = connected, `─` = blocked
- Icons: `你`(player) `·`(empty) `👾`(enemy) `🎁`(treasure) `🚪`(exit)

**Display sizing:** Each room icon is exactly 5 chars wide to match the `─────` border width. Horizontal separators are 1 char.

### Dungeon menu

```
┌── 操作 ─────────┐
│ ① · 角色状态    │
│ ② · 背包        │
│ M · 查看地图     │
│ 3 · ↓ 下         │
│ 4 · → 右         │
│ R · 返回地面     │
└─────────────────┘
```

**Movement command indexing:** Since ①②M are prefix options, movement options start at index 3. Code must offset: `n = int(cmd) - 3; moves[n]`.

### Multi-floor progression

When player reaches the exit room (content == "exit"):
1. Show option: enter next floor or return to surface
2. Next floor → generate new `Dungeon(floor=current+1)` with stronger enemies
3. Return → back to wilderness menu

Enemy scaling per floor: `character.level + (floor - 1)` — adds level bonus.

### Room events — auto-triggered on entry

Player enters a room, then:
1. If content is enemy → auto-start `interactive_battle`
2. If content is treasure → auto-reward (no choice)
3. If content is exit → prompt for next floor
4. If content is empty → show movement menu

After battle (win or loss), room content becomes "empty" so it doesn't re-trigger.

## File refactoring pattern (monolith → package)

When a single `.py` file exceeds 500+ lines:

### Package structure

```
project/
├── run.py                          # Entry: `from package.main import main_loop; main_loop()`
└── package/
    ├── __init__.py                 # Empty
    ├── data.py                     # Constants: skills, items, materials, monster names
    ├── character.py                # Main_character class (only imports from data)
    ├── items.py                    # Item functions (use_item, equip_item, backpack_menu, try_add_item)
    ├── battle.py                   # Monster, EliteMonster, interactive_battle
    ├── dungeon.py                  # DungeonRoom, Dungeon
    ├── locations.py                # Location, MainCity, Wilderness, Map
    └── main.py                     # create_character, main_loop, entry
```

### Import rules to avoid circular imports

- `data.py` → no imports (pure constants)
- `character.py` → imports from `data.py` only
- `items.py` → imports from `data`, `character`
- `battle.py` → imports from `data`, `character`, `items`
- `dungeon.py` → imports from `battle`, `data`, `character`, `items`
- `locations.py` → imports from `dungeon`, `battle`, `character`, `items`, `data` (lazy import Dungeon inside the method that uses it)
- `main.py` → imports from `locations`, `character`, `items`, `data`

**Key rule:** `character.py` must NOT import from modules that import character (no circular chain). Keep character self-contained with `data.py` only.

### Lazy import for recursive dependencies

`locations.py:Wilderness.explore()` needs `Dungeon` but `dungeon.py` imports battle → items → character. Since character → data only (no circle), just do:

```python
class Wilderness(Location):
    def explore(self, character):
        from .dungeon import Dungeon  # lazy import inside method
        dungeon = Dungeon(floor=1)
```

### Testing after refactoring

```python
from package.character import Main_character
from package.dungeon import Dungeon
from package.battle import Monster, interactive_battle
```

Avoid `from package import *` — explicit imports prevent missing module errors.

```python
LOCATION_ACTIONS = {
    MainCity: [("④","休息","补满HP/MP"),("⑤","锻炼","+10经验"),("⑥","商店","购买道具")],
    Wilderness: [("④","探索","战斗/宝箱")],
}
# Universal actions: ①状态 ②地图 ③移动 ⑦背包 ⑧退出
```

Each location shows **only its available actions**. Movement shows numbered destination list instead of requiring typed names.

## Game loop structure

```
① 角色状态 — shows stats + skill list + backpack usage
② 地图 — lists all locations with descriptions
③ 移动 — shows numbered list of reachable locations
⑦ 背包 — view/use/equip/discard items
⑧ 退出
```

Location-specific actions (④⑤⑥) change dynamically based on `isinstance()`.

## Ad-hoc verification pattern

For each new system, write a focused verification script:

```python
# C:/Users/Windows/AppData/Local/Temp/hermes-verify-X.py
"""Ad-hoc verification: system X"""
import sys
exec(open('模拟.py').read().split("if __name__")[0])
errors = []
# ... test assertions ...
if errors:
    for e in errors: print(f"  • {e}")
    sys.exit(1)
else:
    print(f"✅ All passed")
```

**Clean up temp files** after verification: `rm -f "C:...temp/hermes-verify-*.py"`

## Pitfalls
- **Module-level code runs on import**: `create_character()` at module level calls `input()`. Guard with `if __name__ == "__main__":` or use `exec(read().split("if __name__")[0])` in tests
- **Occupation name mismatch**: the occupation list and the if/elif checks must use identical strings
- **EXP formula precision**: `int()` floors; `round()` gives the mathematically correct geometric sequence
- **copy.deepcopy for backpack items**: without deepcopy, multiple purchases of the same shop item point to the same dict
- **interactive_battle + input() in tests**: use `io.StringIO` to mock stdin: `sys.stdin = io.StringIO('0\n')`
- **Backpack full check**: always check `len(backpack) < backpack_max` before adding; handle both "discard old" and "abandon new" paths
- **Skill buff reset**: `character.buff` must reset to 1.0 at the start of each battle turn, or the buff carries over forever
- **Death stat recalculation**: after death, recalculate `max_hp/max_mp/attack/spell_power` from `INIT_STATS + STAT_PER_LEVEL × (level-1)` — don't use the current values which include equipment bonuses
- **escape vs. player_attack_action return**: return `("escape", None)` as a sentinel that the battle loop checks with `if dmg == "escape"`. Don't use a numeric value that could be confused with real damage
- **Respawn flag placement**: check `character._respawn` at the **top** of the main game loop (before printing location/menu), not after command processing. Use a **standalone `if`** — never chain it as `elif isinstance(...)` with location-specific actions, or it will intercept the user's next command.
- **Monster base_name for drops**: store `self.base_name` before prefixing with "精英" so material lookup still works for elite monsters
- **Escape test with io.StringIO**: provide 15–20 `'E\\\\n'` inputs since 40% of escape attempts fail; a single `'E\\\\n'` will EOFError on failure

## Save / Load system (JSON-based)

### Save data format

```python
SAVES_FILE = os.path.join(project_dir, "saves.json")

def make_save_data(character):
    return {
        "id": f"{character.name}_{character.occupation}",
        "name": character.name, "occupation": character.occupation,
        "level": character.level, "exp": character.exp,
        "hp": character.hp, "max_hp": character.max_hp,
        "mp": character.mp, "max_mp": character.max_mp,
        "attack": character.attack, "spell_power": character.spell_power,
        "gold": character.gold, "backpack_max": character.backpack_max,
        "backpack": [{"name":s["item"]["name"], "count":s["count"], ...} for s in character.backpack],
        "equipment": {key: eq_data if eq else None for key, eq in character.equipment.items()},
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
```

### Overwrite detection

Same-character saves overwrite by matching `id`:
```python
saves = load_saves()
for i, s in enumerate(saves):
    if s["id"] == save_data["id"]:
        saves[i] = save_data; break
else:
    saves.append(save_data)
save_saves(saves)
```

### Restore character from save

```python
def restore_character(save_data):
    c = Main_character(save_data["name"], save_data["occupation"])
    c.level = save_data["level"]; c.exp = save_data["exp"]
    c.hp = save_data["hp"]; c.max_hp = save_data["max_hp"]
    c.backpack = [{"item": item_dict, "count": bd["count"]} for bd in save_data["backpack"]]
    for key in c.equipment:
        c.equipment[key] = restore_item(save_data["equipment"].get(key))
    return c
```

## Dungeon UI patterns (web frontend)

### Always show 4 direction buttons

In the dungeon, display all four ↑↓←→ buttons regardless of available connections. Gray out unusable directions:

```javascript
const dirOrder = {w:'↑', s:'↓', a:'←', d:'→'};
const dirKeys = ['w', 's', 'a', 'd'];
dirKeys.forEach(k => {
  const m = moves.find(x => x.key === k);
  const disabled = !m;
  btns.push({
    text: dirOrder[k],
    cls: 'btn' + (disabled ? ' disabled' : ''),
    act: disabled ? '' : 'dungeon_move',
    payload: disabled ? {} : {key: k}
  });
});
```

CSS for disabled buttons: `.btn.disabled{opacity:.3;cursor:default;background:#111;border-color:#222;color:#555}`

### Exit room shows all options simultaneously

In the exit room, show direction buttons alongside exit actions (next floor, return to surface) so the player can move away and explore more before leaving.

### Fog-of-war connection display

Show connections only between rooms that have BOTH been explored. Unexplored rooms show `?` with no connections. Use `and` (not `or`) for connection visibility:
```python
conn = r and nr and (nx, ny) in r.conn and r.explored and nr.explored
```

This prevents "map revealing" paths to rooms the player hasn't visited.

### Frontend: WASD + directional menu in dungeon

Use w/a/s/d keys for movement, i for status, b for backpack, m for map, r for return. Show direction arrows (↑↓←→) in the menu for clarity while keeping WASD as the input.
