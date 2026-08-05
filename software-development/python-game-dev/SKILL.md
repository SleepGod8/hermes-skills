---
name: python-game-dev
description: Build text-based RPG games in Python — character systems, combat, inventory, equipment, dungeons, economy, loot, and penalties.
trigger: user asks to build, extend, or debug a text-based RPG / roguelike / adventure game in Python
---

# Python Text-Based Game Development

## Architecture Patterns

### Class Separation
- **Character class** (`Main_character`): owns stats, level, exp, gold, backpack, equipment slots
- **Location classes**: base `Location` → `MainCity`, `Wilderness`, etc. Each has location-specific methods (rest, shop, explore)
- **Monster classes**: base `Monster` → `EliteMonster`. Monster stores `base_name` for loot mapping
- **Item data**: flat dicts with keys: `name`, `desc`, `effect` (field, value tuple), `cat` (消耗品/装备/素材/特殊), `price`, `value` (sell price), optional `slot`/`classes`
- **Dungeon**: `DungeonRoom` + `Dungeon` classes. Dungeon has `_generate()`, `show_map()`, `available_moves()`, `enter_room()`, `trigger_event()`

### Data Flow
```
main_loop → location actions → character mutations → loop back
```

## Combat System

```python
def player_attack_action(character):
    """Returns (damage, used_skill). Escape returns ("escape", False)."""
    # Show skills available at current level
    avail = [s for s in SKILL_DATA[character.occupation] if character.level >= s["lv"]]
    # Display menu: 0=normal, 1..N=skills, E=escape
```

```python
def interactive_battle(character, monster):
    """Returns "win", "escape", or "death"."""
    # Turn loop: player attacks → monster counterattacks
    # Escape: 60% success → halve HP/MP/gold, lose 1-3 backpack stacks
    # Death: clear all, _respawn=True
```

## Skill Data Model

```python
SKILL_DATA = {
    'occupation': [
        {"name":"SkillName","lv":1,"mp":0,"desc":"description","type":"dmg","mult":1.5},
        {"name":"BuffSkill","lv":5,"mp":10,"desc":"defense","type":"buff","def_mult":0.5},
    ]
}
```

### Skill types: `dmg` (damage), `multi` (multi-hit), `buff` (defense), `re_mp` (restore MP), `re_hp` (restore HP)

#### `re_mp` / `re_hp` in Web Server

Pitfall: These must be handled in `player_turn()` before the fallthrough else clause. Without handling, they deal damage instead of restoring:

```python
elif skill["type"] == "re_mp":
    heal = int(character.max_mp * skill.get("pct", 0.3))
    character.mp = min(character.mp + heal, character.max_mp)
    return f"💙 恢复 {heal} MP", False
elif skill["type"] == "re_hp":
    heal = int(character.max_hp * skill.get("pct", 0.25))
    character.hp = min(character.hp + heal, character.max_hp)
    return f"💚 恢复 {heal} HP", False
```

#### Item Use in Battle → Monster Counter-Attack

After using a consumable during combat, trigger monster_turn():

```python
if gs.fighting and gs.enemy and gs.enemy.hp > 0:
    msg2, death = monster_turn(c, gs.enemy)
    gs.add_msg(msg2)
    if death: apply_death_penalty(c, gs)
```

#### Sell All Action

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

#### MP-Insufficient Skills Grayed Out

Frontend: check sk.mp > STATE.mp, add .disabled class:

```javascript
const noMP = sk.mp > STATE.mp;
btns.push({text: `⚡ ${sk.name}`, cls: 'btn' + (noMP ? ' disabled' : ''),
           act: noMP ? '' : 'battle_attack', payload: {skill: i}});
```

#### Dynamic Backpack Price in Shop

Frontend must calculate real-time price from STATE.backpack_max:

```javascript
if (it.name === '扩容背包') {
  const purchases = Math.floor((STATE.backpack_max - 10) / 5);
  price = Math.floor(500 * Math.pow(1.5, purchases));
  priceText = `${price}金（已扩容${purchases}次）`;
}
```

### Multi-Turn Buff Skills

A `buff` skill with a `turns` field creates a **multi-turn damage reduction**. The buff value (`def_mult`, e.g. 0.5 = 50% damage taken) persists for N turns, then resets to 1.0:

```python
# Skill data
{"name":"铁壁", "lv":5, "mp":10, "desc":"3回合减伤50%",
 "type":"buff", "def_mult":0.5, "turns":3}
```

**Web server** — `player_turn()` returns immediately (no monster damage on buff turn):
```python
elif skill["type"] == "buff":
    character.buff = skill.get("def_mult", 0.5)
    character.buff_turns = skill.get("turns", 1)
    pct = int((1 - character.buff) * 100)
    return f"🛡️ {name} 释放【{skill['name']}】，{character.buff_turns}回合减伤{pct}%", False
```

**`monster_turn()`** — applies buff to incoming damage, decrements counter:
```python
def monster_turn(character, monster):
    buff = getattr(character, 'buff', 1.0)
    dmg = int(max(1, monster.attack + randint(-2, 2)) * buff)
    character.hp -= dmg
    bt = getattr(character, 'buff_turns', 0)
    character.buff_turns = max(0, bt - 1)
    if character.buff_turns <= 0: character.buff = 1.0
    return (f"{name} 反击！造成 {dmg} 点伤害", character.hp <= 0)
```

**Terminal** — `interactive_battle()` resets buff at turn start only if `buff_turns` expired:
```python
character.buff = 1.0
bt = getattr(character, 'buff_turns', 0)
if bt > 0:
    character.buff_turns = bt - 1
    if character.buff_turns <= 0: character.buff = 1.0
```

**Pitfall**: `character.buff` and `character.buff_turns` are dynamically set attributes (not in `__init__`). Use `getattr()` with defaults when reading, not direct attribute access.

## Backpack / Inventory

### Stacking Rules
- Per-category stack limits: `STACK_MAX` (consumables=5), `STACK_MAX_MAT` (materials=10)
- Equipment never stacks (count always 1)
- Backpack is list of `{"item": item_dict, "count": int}`
- `try_add_item()` checks for existing partial stack first, then new slot

### Backpack Menu
```
U · 使用/装备   D · 丢弃
S · 售卖 (at shop)
```
- Using consumable: decrement count, remove stack at 0
- Equipping: calls `equip_item()`, decrement count
- Discard from stack: ask quantity or "a" for all

## Equipment System

- 4 slots: `weapon`, `offhand`, `armor`, `accessory`
- Each equipment item has: `slot`, `classes` (list of allowed occupations, or None for all)
- `equip_item()`:
  1. Check class restriction — reject if occupation not in allowed
  2. If slot occupied: `apply_effect(old, add=False)` → put old in backpack → `apply_effect(new, add=True)`
- `apply_effect(character, field, val, add=True)`: handles attack/spell_power/max_hp/max_mp

## Dungeon System

### Generation (Union-Find + BFS)
```python
# 1. Create 5×5 grid rooms
# 2. Union-Find spanning tree (guarantees connectivity)
# 3. Add 20% extra random edges for variety
# 4. BFS from (0,0) → place exit at farthest room
# 5. Random room contents: 55% enemy, 30% empty, 15% treasure
# 6. Random start position (NOT exit): forced to "empty" content
starts = [p for p in self.rooms if p != exit_pos]
start = random.choice(starts)
self.px, self.py = start
self.rooms[start].content = "empty"      # ← MUST force empty, else start may have enemy!
self.rooms[start].explored = True
```

### Dungeon Map for Web Frontend (CSS Grid 9×9)

For the web frontend, render the dungeon as a 9×9 CSS grid where:

- Every even (x,y) cell = room cell (positions 0,0 to 4,4)
- Odd-x, even-y cells = horizontal connections between rooms
- Even-x, odd-y cells = vertical connections between rooms
- Odd-x, odd-y cells = empty spaces (grid filler)

**Backend must compute `conn_h` and `conn_v` arrays** and include them in the `dungeon_map` return value. Missing them causes the frontend to show no path lines:

```python
conn_h, conn_v = [], []
for y in range(SIZE):
    for x in range(SIZE):
        r = rooms.get((x, y))
        if x < SIZE - 1:
            nr = rooms.get((x+1, y))
            conn_h.append(bool(r and nr and (x+1, y) in r.conn and r.explored and nr.explored))
        if y < SIZE - 1:
            dr = rooms.get((x, y+1))
            conn_v.append(bool(r and dr and (x, y+1) in r.conn and r.explored and dr.explored))
```

**Frontend renders connections with colored symbols:**

```javascript
// Horizontal: idx = ry*4 + rx, where rx = (x-1)/2, ry = y/2
// NOTE: ry*4, NOT ry*5 — each row has only 4 horizontal connections!
const show = dm.conn_h[idx];
// Show '─' in #4a8a5a (green) if connected, ' ' in #222 if not

// Vertical: idx = ry*5 + rx, where rx = x/2, ry = (y-1)/2
// Vertical: ry*5 IS correct — each column has 5 vertical connections
const show = dm.conn_v[idx];
// Show '│' in #4a8a5a (green) if connected, ' ' in #222 if not
```

**CRITICAL: Backend array layout (index pitfall)**

The `conn_h` array has 5 rows × 4 connections = 20 items, indexed as:
```
row 0: conn_h[0..3]  (connections between columns 0-1, 1-2, 2-3, 3-4)
row 1: conn_h[4..7]
...
row 4: conn_h[16..19]
```

The `conn_v` array has 4 rows × 5 connections = 20 items, indexed as:
```
col 0: conn_v[0]  (row 0-1), conn_v[5] (row 1-2), conn_v[10] (row 2-3), conn_v[15] (row 3-4)
col 1: conn_v[1], conn_v[6], conn_v[11], conn_v[16]
...
col 4: conn_v[4], conn_v[9], conn_v[14], conn_v[19]
```

**Horizontal formula `ry*4 + rx`** (NOT `ry*5 + rx` — the latter causes index shift of +1 per row after the first, misaligning all paths).

### Exit Room UI (Web)

The exit room should show **both** movement direction buttons AND exit options simultaneously, so the player can choose to walk away (continue exploring) without being forced into next-floor/return:

```javascript
if (di) {
  // Direction buttons must use FIXED order: ↑ ↓ ← → (w s a d)
  // NOT moves.forEach() which iterates in random dict order!
  const dirOrder = {w:'↑',s:'↓',a:'←',d:'→'};
  const dirKeys = ['w','s','a','d'];
  dirKeys.forEach(k => {
    const m = moves.find(x => x.key === k);
    if (m) btns.push({text: dirOrder[k], act:'dungeon_move', payload:{key:k}});
  });
  if (di.content === 'exit') {
    btns.push({text:'⬇️ 下一层', act:'next_floor'});       // Plus exit options
    btns.push({text:'🚶 返回地面', act:'dungeon_leave'});
  }
}
```

### Map Display with Fog of War
- 5-char wide cells matching `─────` border width
- Icons: ` 你  ` (player), `  ·  ` (empty), ` 👾 ` (enemy), ` 🎁 ` (treasure), ` 🚪 ` (exit), `  ?  ` (unexplored)
- Horizontal connection: ` ` (space) between cells if connected, `│` if not
- Vertical connection: `──│──` in border if connected, `─────` if not
- Only explored rooms shown; unexplored show as `?`
- Legend at bottom of map

### Room Events
- Enemy: random `Monster` or `EliteMonster` (15%), call `interactive_battle()`
- Treasure: EXP + gold + 60% chance of random loot item
- Exit: offer choice to descend (higher floor = stronger enemies) or return to surface

## Economy System

- Items have `price` (buy) and `value` (sell = 80% of buy for shop items)
- Materials: lowest value (2-5 gold)
- Consumables: medium value
- Equipment: highest value
- Monster gold drops: reduced to `level * randint(1,2)`
- Shop has two modes: buy and sell

### Backpack Expansion Price Scaling

When the player buys backpack expansion multiple times, the price should **increase geometrically** (not stay flat) to prevent trivial infinite inventory. **Infer purchase count from `backpack_max`** rather than tracking a separate counter — this avoids desyncs and saves correctly:

```python
# Infer purchases from current capacity (starts at 10, +5 per purchase)
purchases = (character.backpack_max - 10) // 5
price = int(500 * (1.5 ** purchases))  # 500, 750, 1125, 1687, 2531, ...

if character.gold < price:
    gs.add_msg(f"❌ 金币不足！需要 {price}金")
else:
    character.gold -= price
    character.backpack_max += 5
    gs.add_msg(f"🎒 背包扩容！花费{price}金，当前{character.backpack_max}格")
```

**Formula**: `price = BASE * RATE^purchases`, where `BASE=500`, `RATE=1.5`. This gives ~50% price increase per purchase. Starting at 500 gold means ~2-3 dungeon runs before the first upgrade.

**Pitfall**: Do NOT track purchases via `getattr(character, 'backpack_purchases', 0)` — that attribute won't survive save/load. Always infer from `backpack_max` which is part of the normal save data.

## Drop / Loot System

- Monster drops after victory: 5% equipment, 70% material, 25% nothing
- Materials keyed by `monster.base_name` via `MONSTER_MATERIALS` dict
- Treasure loot from `TREASURE_LOOT` list

## Enemy Scaling — Floor-Based (Not Player-Level)

Instead of scaling enemies to player level (which makes all content equally challenging regardless of depth), scale enemies to **dungeon floor only**, then apply **reward penalties** for high-level players farming low floors.

### Monster Stats by Floor

```python
s = 1.0 + (floor - 1) * 0.8  # floor 1=1.0, floor 2=1.8, floor 3=2.6...
self.hp = int(random.randint(20, 35) * s)
self.attack = int(random.randint(4, 8) * s)
```

### Reward Decay Formula

```python
def _reward_mult(player_level, floor_level):
    # Caps at 1.0 (full) and 0.1 (minimum 10%)
    return min(1.0, max(0.1, 1.0 - (player_level - floor_level * 2 - 1) * 0.2))
```

| Scenario | Multiplier | Meaning |
|----------|-----------|---------|
| Lv.1 on F1 | 1.0 | Full rewards |
| Lv.5 on F1 | 0.6 | 40% penalty — too strong for first floor |
| Lv.5 on F3 | 1.0 | Full rewards — appropriate depth |
| Lv.10 on F1 | 0.1 | Heavy penalty (min 10%) |
| Lv.10 on F5 | 1.0 | Full — F5 is appropriate |

The thresholds mean: **expected floor ≈ player_level / 2**. Players must descend to maintain reward efficiency.

### Reward Methods on Monster

Monsters expose reward calculation methods that accept `player_level`:

```python
class Monster:
    def reward_exp(self, player_level):
        base = int(round(100 * (1.5 ** (self.floor_level - 1)) * random.uniform(0.15, 0.25)))
        return int(base * _reward_mult(player_level, self.floor_level))

    def reward_gold(self, player_level):
        base = self.floor_level * random.randint(1, 2)
        return int(base * _reward_mult(player_level, self.floor_level))
```

### Reset on Re-Entry

Each `Dungeon(floor=1)` call creates a completely fresh dungeon. Players re-entering the dungeon start at floor 1 with weak enemies and low base rewards.

### Integration Points

- **server.py `dungeon_move`**: `Monster(lv)` where `lv = gs.dungeon.floor` (NOT `c.level + lv - 1`)
- **server.py `battle_attack`**: `m.reward_exp(c.level)` + `m.reward_gold(c.level)` instead of hardcoded formulas
- **dungeon.py `trigger_event`**: same — pass `self.floor` instead of `character.level`

## Multi-Hit Skill Damage (`multi` type)

In the web server's `player_turn()`, the `multi` skill type must loop over `hits` and sum damage:

```python
elif skill["type"] == "multi":
    hits = skill.get("hits", 2); total = 0; parts = []
    for h in range(hits):
        d = max(1, int(character.attack * skill.get("mult", 1.5)))
        total += d; parts.append(f"第{h+1}击{d}伤")
    dmg = total
    msg = f"⚡ {character.name} 使用 {skill['name']}！{' '.join(parts)} 总计 {dmg} 点伤害"
elif skill["type"] == "magic":
    ...
else:
    dmg = int(character.attack * skill.get("mult", 1.0))
if 'msg' not in dir(): msg = f"...{dmg}..."  # fallback for dmg/magic types
```

Without this handling, `multi` falls into the `else` clause and deals only one hit (1.5x instead of 3x for two hits), making multi-hit skills weaker than single-hit ones — the opposite of the design intent.

## Death Penalty

```python
# On death (HP ≤ 0 in battle):
character.backpack.clear()
for slot in character.equipment: character.equipment[slot] = None
character.gold = 0; character.hp = 1; character.mp = 1; character.exp = 0
# Reset stats to base + level growth (remove equipment bonuses)
character._respawn = True  # Checked in main loop → teleport to main city
```

## Fail / Escape Penalty

- Escape success: 60% chance
- On success: halve HP/MP/gold, randomly lose 1-3 backpack stacks
- On failure: monster gets free attack, turn continues

## Dungeon Navigation (WASD)

- Movement: `w/a/s/d` (↑↓←→ arrows shown as hints)
- Status: `i`, Backpack: `b`, Map: `m`, Return: `r`
- `r` only works in the **exit room**; elsewhere shows "❌ 只有出口房间才能返回地面"
- Exit room offers: 1) next floor, 2) return to surface, 0) cancel
- Exit room content (`room.content = "exit"`) is **never modified** — player can leave and return repeatedly

### Random Starting Position

```python
# After generation, pick random room (not exit) as start
starts = [p for p in self.rooms if p != exit_pos]
start = random.choice(starts)
self.px, self.py = start
self.rooms[start].explored = True
```

### Map Connection Display

- Show path ` ` (space) between rooms ONLY if **both** rooms have been explored AND are actually connected
- Show `│` if NOT connected (regardless of exploration)
- No ambiguous `·` symbol — only two states: connected=space, blocked=│
- **Pitfall**: using `(r.explored or nr.explored)` reveals paths to unexplored rooms, spoiling the fog of war. Always use `(r.explored and nr.explored)` so paths only appear between explored rooms.

## Module Refactoring (Monolith → Package)

When a single game file exceeds ~200 lines, split into a package:

```
land_of_heroes/
├── __init__.py      # empty
├── data.py           # constants, skill/item/material data (no imports)
├── character.py      # Main_character class (imports from data only)
├── items.py          # item/equip/backpack functions (imports data, character)
├── battle.py         # Monster, battle functions (imports data, character, items)
├── dungeon.py        # Dungeon generation (imports data, battle, items)
├── locations.py      # Location subclasses, Map (imports data, items, dungeon)
└── main.py           # create_character, main_loop, entry
run.py                # from land_of_heroes.main import main_loop; main_loop()
```

**Import chain** (avoids circular deps):
- `data.py` → nothing
- `character.py` → data only
- `items.py` → data, character
- `battle.py` → data, character, items
- `dungeon.py` → data, battle, items
- `locations.py` → data, items, dungeon (dungeon imported inside method to avoid circular init)
- `main.py` → character, locations, items

### Building a Web Frontend (FastAPI + HTML/CSS/JS)

When wrapping a terminal RPG as a web application, you need an **event-driven state model** instead of the synchronous `input()` loop.

### Shop Modal (Web)

In the web frontend, implement the shop as a **modal dialog** with buy/sell sections. **Never hardcode shop items in the frontend** — add a `/api/shop-items` endpoint so the frontend fetches the same list the backend uses:

```python
@app.get("/api/shop-items")
def get_shop_items():
    items = []
    for it in SHOP_ITEMS:
        items.append({"name": it["name"], "desc": it["desc"], "price": it["price"],
                       "cat": it.get("cat",""), "slot": it.get("slot",""),
                       "classes": it.get("classes")})
    return {"items": items}
```

```javascript
function openShop() {
  const items = [
    {name:'生命药水', desc:'+30HP', price:20, cat:'消耗品'},
    // ... all shop items
  ];
  let html = `<h3>🏪 兵器铺 · 💰${STATE.gold}金</h3>`;
  html += '━━━ 商品 ━━━';
  items.forEach((it, i) => {
    html += `<div>${it.name} ${it.desc} ${it.price}金<button onclick="buyItem(${i})">购买</button></div>`;
  });
  // Sell section for backpack items with value > 0
  STATE.backpack.forEach((it, i) => {
    if (it.value > 0) {
      html += `<div>${it.name} 售${it.value}金<button onclick="sellItem(${i})">售卖</button></div>`;
    }
  });
  document.getElementById('shop-modal-content').innerHTML = html;
  document.getElementById('shop-modal').classList.add('show');
}

async function buyItem(idx) {
  await action('buy', {index: idx});
  STATE = await (await fetch(`/api/state/${SID}`)).json();
  openShop();  // Re-render with updated gold
}
```

**Pitfall**: Never call `fetch('/api/new-game')` in the shop — that creates a new game session and wipes all progress. Always use `action('buy')` / `action('sell')` + refresh state.

### Architecture

```
Frontend (HTML/JS) ↔ FastAPI API ↔ GameState obj ↔ Game logic classes
```

- **GameState class** holds character, dungeon, location + message buffer
- **API endpoints**: `POST /api/new-game`, `POST /api/action/{sid}`, `GET /api/state/{sid}`
- **Session storage**: in-memory dict keyed by short UUID (`games[sid]`)
- **Frontend**: single HTML file with embedded CSS/JS, fetches state and re-renders on each action

### GameState Design

```python
class GameState:
    def __init__(self, character, dungeon=None):
        self.character = character
        self.dungeon = dungeon
        self.location = "主城"
        self.messages = []  # message buffer for frontend

    def to_dict(self):
        # Serialize character stats, equipment, backpack, dungeon map, etc. to JSON
        # Include dungeon_map (grid), dungeon_moves (WASD), dungeon_info
        # Return messages[-20:] to avoid overflow
```

### API Pattern

```python
from pydantic import BaseModel

class ActionReq(BaseModel):
    action: str
    payload: dict = {}

@app.post("/api/action/{sid}")
def do_action(sid: str, req: ActionReq):
    gs = games.get(sid)
    # Mutate game state based on req.action
    # Each action: validate → mutate → add msg → return gs.to_dict()
    return gs.to_dict()
```

### Save/Load System (JSON File)

Persist game state to a JSON file so progress survives server restarts:

```python
SAVES_FILE = "saves.json"

def load_saves():
    if os.path.exists(SAVES_FILE):
        with open(SAVES_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("saves", [])
    return []

def save_saves(saves_list):
    with open(SAVES_FILE, "w", encoding="utf-8") as f:
        json.dump({"saves": saves_list}, f, ensure_ascii=False, indent=2)
```

**Save data structure** (one entry per character):

```python
{
    "id": f"{character.name}_{character.occupation}",  # unique key for overwrite
    "name": "...", "occupation": "...",
    "level": N, "exp": N,
    "hp": N, "max_hp": N, "mp": N, "max_mp": N,
    "attack": N, "spell_power": N,
    "gold": N, "backpack_max": N,
    "backpack": [{"name": "...", "count": N, ...}],
    "equipment": {"weapon": {...} or None, "offhand": ..., "armor": ..., "accessory": ...},
    "saved_at": "2026-07-24 10:00",
}
```

**Restore logic**: reconstruct a `Main_character` instance from save data, then manually set all fields (since the constructor uses defaults).

**Overwrite vs append**: key by `id` (name + occupation). If an existing save has the same `id`, replace it; otherwise append.

**API endpoints**:
- `GET /api/saves` → list all saves
- `POST /api/save/{sid}` → save current session's character (overwrite by id)
- `POST /api/load/{save_id}` → restore character and create new session
- `POST /api/delete-save/{save_id}` → remove a save

**Frontend: saves list on create screen**:

```javascript
fetch('/api/saves').then(r=>r.json()).then(data => {
  data.saves.forEach(s => {
    // Show "读取" (load) and "删除" (delete with confirm) buttons
    renderSaveRow(s);
  });
});
```

**Return to home screen** (without browser refresh):

```javascript
function goHome() {
  document.getElementById('game-screen').style.display = 'none';
  document.getElementById('create-screen').style.display = 'flex';
  STATE = null; SID = null;
  loadSaves();  // refresh save list
}
```

### Disabled Direction Buttons

For a cleaner dungeon UI, always show all 4 direction buttons (↑ ↓ ← →) and disable the ones where movement is unavailable:

```javascript
const dirOrder = {w:'↑', s:'↓', a:'←', d:'→'};
const dirKeys = ['w', 's', 'a', 'd'];
dirKeys.forEach(k => {
  const m = moves.find(x => x.key === k);
  const disabled = !m;
  btns.push({text: dirOrder[k], cls: 'btn' + (disabled ? ' disabled' : ''),
             act: disabled ? '' : 'dungeon_move', payload: disabled ? {} : {key:k}});
});
```

CSS for disabled state:
```css
.btn.disabled{opacity:.3;cursor:default;background:#111;border-color:#222;color:#555}
```

### Frontend Tips

- **State-driven rendering**: single `render()` function that redraws all panels from `STATE`
- **Character creation**: separate screen with occupation cards, then switch to game screen
- **HP/MP bars**: CSS gradient bars with inline `width:%` style
- **Dungeon map**: CSS grid (`grid-template-columns: repeat(5, 44px)`) populated from `dungeon_map.grid`
- **Action buttons**: dynamic button generation from game state (buttons differ in main city vs dungeon vs exit room)
- **Modals**: backpack and shop as CSS modals (`.modal.show` toggle)
- **No page reloads**: every action is `fetch()` → update `STATE` → `render()`

### Key Differences from Terminal Loop

| Terminal | Web |
|----------|-----|
| `while True:` blocking loop | Stateless API calls |
| `input()` waits for user | Button click triggers API |
| `print()` to output | Message buffer → frontend renders |
| Global variables per session | `GameState` objects in dict |
| Keyboard: `w/a/s/d` | Buttons: `↑ ↓ ← →` |

### Web Battle System (Step-based)

The terminal's `interactive_battle()` uses `input()` and cannot be reused in a web API. Implement a **step-based battle** instead:

```python
def player_turn(character, monster, skill=None):
    """Returns (msg, is_victory)"""
    dmg = calc_damage(character, monster, skill)
    monster.hp -= dmg
    return (f"造成 {dmg} 点伤害", monster.hp <= 0)

def monster_turn(character, monster):
    """Returns (msg, is_death)"""
    dmg = max(1, monster.attack + randint(-2, 2))
    character.hp -= dmg
    return (f"反击 {dmg} 点伤害", character.hp <= 0)

# API handler:
if act == "battle_attack":
    skill_idx = pay.get("skill", -1)
    msg, victory = player_turn(c, gs.enemy, skill)
    gs.add_msg(msg)
    if victory:
        gs.fighting = False; gs.enemy = None
    else:
        msg2, death = monster_turn(c, gs.enemy)
        gs.add_msg(msg2)
        if death:
            apply_death_penalty(c); gs.dungeon = None
```

**GameState fields for battle:**
```python
self.fighting = False  # blocks movement when True
self.enemy = None      # Monster instance
```

**Frontend: when `fighting == True`**, clear movement buttons, show attack + skill buttons, render enemy panel with HP bar.

### Frontend Battle UI

```javascript
if (STATE.fighting && STATE.enemy) {
  btns = [];
  btns.push({text:'⚔️ 普通攻击', act:'battle_attack', payload:{skill:-1}});
  STATE.skills.forEach((sk, i) => {
    btns.push({text:`⚡ ${sk.name}`, act:'battle_attack', payload:{skill:i}});
  });
}
```

### Frontend Button Binding (Avoid onclick quoting bugs)

Never build inline `onclick="action('name', {"key":"val"})"` — inner JSON double quotes break the HTML attribute. Use **data attributes**:

```javascript
// Generate buttons
el.innerHTML = btns.map(b => {
  const payload = JSON.stringify(b.payload || {});
  return `<button data-act="${b.act}" data-payload='${payload}'>${b.text}</button>`;
}).join('');

// Bind events
el.querySelectorAll('[data-act]').forEach(btn => {
  btn.onclick = () => {
    const act = btn.dataset.act;
    const payload = JSON.parse(btn.dataset.payload || '{}');
    action(act, payload);  // fetch→update STATE→render()
  };
});
```

### Frontend Enemy HP Bar

Display enemy HP visually using CSS gradient bars, same style as player HP:

```html
<div style="background:#222;border-radius:4px;overflow:hidden;height:12px">
  <div style="height:100%;width:${hpPct}%;background:linear-gradient(90deg,#c0392b,#e74c3c)"></div>
</div>
```

### Skills as Objects in API Response

When `to_dict()` returns skills, they may be dicts (with `name`, `desc`, `mp`, `mult`, etc.) instead of plain strings. The frontend must use `sk.name` not `${sk}`:

```javascript
// ❌ Wrong — prints "[object Object]"
const skills = s.skills.map(sk => `<span>${sk}</span>`).join('');

// ✅ Correct
const skills = s.skills.map(sk => `<span>${sk.name}</span>`).join(' ');
```

### API Action Naming Consistency

Action names in the frontend must exactly match the backend's `elif act == "..."` condition. A typo like `_next_floor` vs `next_floor` silently fails (no match, falls to `else: "未知操作"`). Keep a single source of truth:

```javascript
// Frontend action names must match server.py exactly
btns.push({text:'⬇️ 下一层', act:'next_floor'});          // NOT '_next_floor'
btns.push({text:'🚶 返回地面', act:'dungeon_leave'});       // NOT 'dungeon_return'
```

### Browser Caching After HTML Edits

After editing `static/index.html`, the browser may serve a cached version (`304 Not Modified`). Verify the new version is live:

```bash
curl -s http://localhost:8080/ | wc -c
# Compare to file size: wc -c static/index.html
```

If sizes differ, the old file is cached. Hard refresh (`Ctrl+F5`) or add `-H "Cache-Control: no-cache"` to curl.

### Server Restart and Session Loss

Server sessions are in-memory (`games[sid]`). Restarting the server loses all active sessions. The frontend will get `404 会话不存在` on the next API call. Mitigation: add graceful error handling in the frontend (`if res.status === 404 → redirect to create screen`).

### Variable Scope After Insertion

When inserting code into an existing function, check that any new variable references are **in scope**:

```javascript
// ❌ Wrong: innerHTML assigned directly, then code tries to append to undefined `html`
function renderState() {
  document.getElementById('state-panel').innerHTML = `...`;  // no `html` variable
  if (condition) {
    html += `<div>more</div>`;  // ReferenceError! html is undefined
  }
  document.getElementById('state-panel').innerHTML = html;  // still undefined
}

// ✅ Correct: use a local variable throughout
function renderState() {
  let html = `...`;
  if (condition) {
    html += `<div>more</div>`;
  }
  document.getElementById('state-panel').innerHTML = html;
}
```

**Rule**: if you refactor `function X() { A; B; }` into `function X() { A; C; B; }` where `C` references a variable that `A` creates, make sure `A` actually assigns to a variable (not directly to a DOM property). When in doubt, use a local variable for the entire function body.

### Missing Function Closing Brace

When inserting a code block between a function body and its closing `}`, verify the closing brace still exists:

```javascript
function renderState() {
  // ... original code ...
  document.getElementById('state-panel').innerHTML = html;
  // ❌ If you add code here, the } below gets displaced!
}  // ← This } MUST still close renderState()

function nextFunction() { ...
```

Always check: the last `}` before the next `function` keyword must match the current function's open brace. Count nesting!

### Pitfalls

- FastAPI endpoints must accept Pydantic models, not raw dicts, for proper body parsing
- `random` module must be imported at module level (not just inside methods) when used across multiple endpoints
- **HTML onclick quoting**: never build inline `onclick="action('name', {...})"` - the inner JSON's double quotes break the HTML attribute. Use `data-act` + `data-payload` attributes with `querySelectorAll('[data-act]')` event binding instead
- **Server caching**: after editing `static/index.html`, the old version may be cached by the browser. Hard refresh (Ctrl+F5) or check via `curl` to confirm the new HTML is served
- Chinese characters in curl/MSYS must be sent as UTF-8 bytes via `printf` + pipe, not inline JSON strings
- Server sessions are in-memory — restarting the server loses all active sessions
- Frontend must handle loading/error states gracefully (API calls can fail mid-game)
- Don't use `import random` only inside a method — import at top of module for global availability

## Main Loop Pattern

```python
while True:
    # Check respawn FIRST (before printing menu)
    if getattr(character, '_respawn', False):
        character._respawn = False
        current_loc = game_map.locations["主城"]
    # Print location header + menu
    cmd = input()
    # Process universal commands (status, map, move, backpack, quit)
    # Process location-specific commands (rest, shop, explore, etc.)
```

## Item Data Format

```python
# Consumable
{"name":"生命药水","desc":"恢复50HP","price":20,"value":16,"effect":("hp",50),"cat":"消耗品"}
# Equipment
{"name":"铁剑","desc":"攻击+3","price":80,"value":64,"effect":("attack",3),"cat":"装备","slot":"weapon","classes":["战士","骑士"]}
# Material
{"name":"狼牙","desc":"从野狼身上获得","value":3,"effect":("none",0),"cat":"素材"}
# Special
{"name":"扩容背包","desc":"背包+5格","price":300,"value":240,"effect":("bp",5),"cat":"特殊"}
```

## Pitfalls

- `_respawn` check must be at TOP of main loop, before the menu print, not inside the elif chain — otherwise menu shows wrong location
- Monster `base_name` must be stored separately from `name` (which gets prefixed "精英" for elites) for material lookup
- When resetting stats on death, recalculate from `INIT_STATS` + level growth, don't just set to base
- Backpack items are stored as `{"item": ..., "count": N}` stacks — all backpack operations (add/use/discard/sell) must handle count properly
- Equipment `equip_item` removes old item's effect (subtracts) before applying new one (adds)
- **Menu index offset**: when menu items (status, backpack, etc.) are added BEFORE movement options, the movement option numbering shifts. Code like `moves[int(cmd)-1]` breaks because `cmd` no longer maps to `moves[0]`. Fix: subtract the menu offset: `n = int(cmd) - menu_offset; moves[n]`
- **Occupation input**: allow both full name and number input; validate against `occupation_list` using index lookup
- **SKILL_DATA lookup uses base_occupation**: Data dicts like `SKILL_DATA` use base occupation keys. After advancement, `character.occupation` changes (e.g., "战士" → "剑圣") but `SKILL_DATA` still has "战士". Always use `character.base_occupation` for dict lookups. Example:
  ```python
  # ❌ WRONG — KeyError after advancement
  avail = [s for s in SKILL_DATA[character.occupation] if character.level >= s["lv"]]
  # ✅ CORRECT — use base_occupation
  avail = [s for s in SKILL_DATA[character.base_occupation] if character.level >= s["lv"]]
  ```
