---
name: fastapi-game-server
description: "Build a web frontend for terminal RPG games using FastAPI — game state management, battle system, dungeon map rendering, save/load, modal UI."
version: 1.1.0
author: agent
license: MIT
tags: [fastapi, game, web, rpg, python, dungeon, state-management]
---

# FastAPI Game Server — Terminal RPG → Web Frontend

Convert a terminal-based Python RPG into a web game with FastAPI backend + SPA frontend.

## When to Use

- You have a terminal RPG using `input()`/`print()` and want a web UI
- Building game-like interactive features (dungeon map, turn-based battle, inventory) as a web app
- Adding save/load, shop, backpack functionality to a web game

## Architecture

```
User's Browser (SPA) ←→ FastAPI (REST) ←→ Game Logic (Python classes)
```

- **Stateful backend**: Game state stored in memory (`games[ session_id ] = GameState`)
- **Stateless API**: Each request carries session_id; backend mutates state and returns full state
- **Frontend**: Single HTML file with embedded CSS/JS, calls API, re-renders on every response

## Core Pattern: GameState Manager

```python
games = {}  # session_id → GameState

class GameState:
    def __init__(self, character):
        self.character = character
        self.dungeon = None
        self.location = "主城"
        self.messages = []
        self.fighting = False
        self.enemy = None

    def to_dict(self):
        """Serialize everything the frontend needs."""
        return {
            "name": self.character.name,
            "hp": self.character.hp, "max_hp": self.character.max_hp,
            "location": self.location,
            "fighting": self.fighting,
            "enemy": self._enemy_info() if self.fighting and self.enemy else None,
            "dungeon_map": self._dungeon_map() if self.dungeon else None,
            "dungeon_moves": self._dungeon_moves() if self.dungeon and not self.fighting else [],
            "dungeon_info": self._dungeon_info() if self.dungeon else None,
            "messages": self.messages[-30:],
        }
```

Key: return the FULL state every time — frontend is a dumb renderer.

## Converting Terminal I/O to API Actions

### Terminal pattern (DO NOT use in web):
```python
# Blocking! input() freezes the API
def battle(character):
    while True:
        cmd = input("请选择: ")  # ← BLOCKS THE THREAD
        ...
```

### Web pattern:
```python
# Step 1: Enter enemy room (creates monster, sets fighting=True)
@app.post("/api/action/{sid}")
def dungeon_move(sid, req):
    gs.enemy = Monster(level)
    gs.fighting = True
    return gs.to_dict()

# Step 2: Player clicks "Attack" → one turn
@app.post("/api/action/{sid}")
def battle_attack(sid, req):
    victory, msg = process_player_turn(gs.character, gs.enemy, skill)
    gs.add_msg(msg)
    if victory:
        gs.fighting = False
        gs.enemy = None
    else:
        death_msg, died = process_monster_turn(gs.character, gs.enemy)
        gs.add_msg(death_msg)
    return gs.to_dict()
```

Each API call is ONE game action. No loops, no `input()`.

## Dungeon Map: 9×9 CSS Grid

Render a 5×5 dungeon grid as a 9×9 CSS grid (rooms at even positions, connectors at odd):

```
┌───┬───┬───┬───┬───┐
│ R │ C │ R │ C │ R │  ← Row: room, horiz-conn, room, horiz-conn, room
├───┼───┼───┼───┼───┤  ← Vertical connectors in border row
│ R │   │ R │   │ R │
```

**Backend** sends conn_h (20 bools: 5 rows × 4 horizontal) and conn_v (20 bools: 4 rows × 5 vertical):
```python
conn_h.append(bool(r and nr and (x+1, y) in r.conn and r.explored and nr.explored))
```

**Frontend** renders with 22px cells:
```javascript
// Room cells at (even x, even y)
// Horizontal connectors at (odd x, even y): idx = row*4 + col
// Vertical connectors at (even x, odd y): idx = col*4 + row
```

**Connection rule** (changed after user feedback): Only show paths between BOTH explored rooms.

## Battle System (Step-based)

Instead of `interactive_battle()` with `input()`, implement turn logic:

### Skill Types Reference

| type | Purpose | Example | Fields |
|------|---------|---------|--------|
| `dmg` | Physical damage | 猛击 | `mult` |
| `magic` | Magic damage | 火球术 | `mult`, `use_sp` |
| `multi` | Multi-hit damage | 连射 | `mult`, `hits` |
| `buff` | Defensive buff | 铁壁 | `def_mult`, `turns` |
| `re_mp` | MP recovery | 法力涌动 | `pct` |
| `re_hp` | HP recovery | 治愈术 | `pct` |

### Normal Attack + Skill Damage

```python
def player_turn(character, monster, skill=None):
    if skill:
        cost = skill.get("mp", 0)
        if character.mp < cost:
            return f"❌ MP不足！需要 {cost}MP", False
        character.mp -= cost
        
        if skill["type"] == "dmg":
            dmg = int(character.attack * skill.get("mult", 1.5))
        elif skill["type"] == "multi":
            hits = skill.get("hits", 2); total = 0
            for h in range(hits):
                d = max(1, int(character.attack * skill.get("mult", 1.5)))
                total += d
            dmg = total
        elif skill["type"] == "magic":
            dmg = int(character.spell_power * skill.get("mult", 2.0))
        elif skill["type"] == "buff":
            character.buff = skill.get("def_mult", 0.5)
            character.buff_turns = skill.get("turns", 1)
            return f"减伤{int((1-buff)*100)}%", False  # No damage
        elif skill["type"] == "re_mp":
            heal = int(character.max_mp * skill.get("pct", 0.3))
            character.mp = min(character.mp + heal, character.max_mp)
            return f"恢复 {heal} MP", False  # No damage
        elif skill["type"] == "re_hp":
            heal = int(character.max_hp * skill.get("pct", 0.25))
            character.hp = min(character.hp + heal, character.max_hp)
            return f"恢复 {heal} HP", False  # No damage
        else:  # Fallback
            dmg = int(character.attack * skill.get("mult", 1.0))
    else:
        dmg = max(1, character.attack + random.randint(-2, 2))
    
    monster.hp -= dmg
    return msg, monster.hp <= 0
```

### Monster Counter-Attack

```python
def monster_turn(character, monster):
    # Apply damage reduction buff
    buff = getattr(character, 'buff', 1.0)
    dmg = max(1, monster.attack + random.randint(-2, 2))
    dmg = int(dmg * buff)
    character.hp -= dmg
    
    # Decrement buff turns
    bt = getattr(character, 'buff_turns', 0)
    character.buff_turns = max(0, bt - 1)
    if character.buff_turns <= 0:
        character.buff = 1.0
    return f"反击{ dmg}点伤害", character.hp <= 0
```

**Key:** Monster turn must fire after EVERY player action — attack, skill, AND item use.

### Item Use During Battle → Enemy Also Acts

When a player uses a consumable item during combat, the monster MUST counter-attack:

```python
if item["cat"] == "消耗品":
    use_item(c, item)
    gs.add_msg(f"💚 使用了 {item['name']}")
    # CRITICAL: monster counter-attacks after item use
    if gs.fighting and gs.enemy and gs.enemy.hp > 0:
        msg2, death = monster_turn(c, gs.enemy)
        gs.add_msg(msg2)
        if death:
            # Handle death...
```

Without this, using a potion during battle gives the player a free turn — the enemy stands still.

### Frontend: MP Check on Skill Buttons

Gray out skills the player can't afford:

```javascript
STATE.skills.forEach((sk, i) => {
    const noMP = sk.mp > STATE.mp;
    btns.push({
        text: `⚡ ${sk.name} [${sk.mp}MP]`,
        cls: 'btn' + (noMP ? ' disabled' : ''),
        act: noMP ? '' : 'battle_attack',
        payload: {skill: i},
        tip: `${sk.desc} (${sk.mp}MP)${noMP ? ' MP不足' : ''}`
    });
});
```

Use `.btn.disabled` CSS class (keeps button in DOM for layout) rather than removing it entirely:

```css
.btn.disabled{opacity:.3;cursor:default;background:#111;border-color:#222;color:#555}
```

Frontend buttons: "普通攻击" + one button per unlocked skill. Each click = one API call.

## Save/Load System

JSON file-based, stored in project root:

```python
SAVES_FILE = os.path.join(BASE_DIR, "saves.json")

def make_save_data(character):     # Serialize: level, exp, hp, mp, gold, backpack[], equipment{}
def restore_character(save_data):  # Deserialize → new Main_character with all stats
```

Save ID = `{name}_{occupation}` — same character name+class overwrites. Load creates a NEW session.

**API endpoints:**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/saves` | GET | List all saves |
| `/api/save/{sid}` | POST | Save current session |
| `/api/load/{save_id}` | POST | Load save → new session |
| `/api/delete-save/{save_id}` | POST | Delete a save |

**Frontend pattern:** On the create screen, fetch saves on load and display them with "读取" and "删除" buttons. Delete requires `confirm()` dialog before calling the API.

## Enemy Scaling (Floor-Based)

**DO NOT** scale enemies with player level. Scale with dungeon floor instead:

```python
def Monster(floor_level):
    s = 1.0 + (floor_level - 1) * 0.8
    self.hp = int(random.randint(20, 35) * s)
    self.attack = int(random.randint(4, 8) * s)
```

Each time player re-enters the dungeon, floor resets to 1 → enemies are weak again.

### Reward Degradation

High-level players farming low floors get reduced rewards:

```python
def _reward_mult(player_level, floor_level):
    """Capped at 1.0 (max), min 0.1 (10%)"""
    return min(1.0, max(0.1, 1.0 - (player_level - floor_level * 2 - 1) * 0.2))
```

| Lv. | Floor | Reward |
|-----|-------|--------|
| 1   | 1     | 100%   |
| 5   | 1     | 60%    |
| 5   | 3     | 100%   |
| 10  | 1     | 10%    |

## Direction Buttons (Always Show 4)

In dungeon, always render ↑ ↓ ← → buttons. Disable (gray out) unavailable directions:

```javascript
const dirOrder = {w:'↑',s:'↓',a:'←',d:'→'};
const dirKeys = ['w','s','a','d'];
dirKeys.forEach(k => {
    const m = moves.find(x => x.key === k);
    const disabled = !m;
    btns.push({text: dirOrder[k], cls: 'btn' + (disabled ? ' disabled' : ''), ...});
});
```

Use CSS `.btn.disabled` class (not HTML `disabled` attribute) to keep buttons in the DOM for layout consistency:

```css
.btn.disabled{opacity:.3;cursor:default;background:#111;border-color:#222;color:#555}
```

## Return to Home (Character Select)

Add a "返回主页面" button in the main city that hides the game screen and shows the create screen, clearing session:

```javascript
function goHome() {
    document.getElementById('game-screen').style.display = 'none';
    document.getElementById('create-screen').style.display = 'flex';
    STATE = null; SID = null;
    loadSaves();
}
```

This lets the player switch characters or delete saves without refreshing the browser.

## Batch Sell (Sell All)

Add a "💰 全部售卖" button in the shop modal. Backend action:

```python
elif act == "sell_all":
    total = 0; names = []
    for s in list(c.backpack):
        val = s["item"].get("value", 0)
        if val > 0:
            total += val * s["count"]
            names.append(f"{s['item']['name']}x{s['count']}")
            c.backpack.remove(s)
    c.gold += total
    gs.add_msg(f"💰 全部售卖！获得 {total}金")
```

Use `list(c.backpack)` to iterate over a copy so `remove()` doesn't skip items. Frontend calls `action('sell_all')` then refreshes state and re-opens shop modal.

## Skill Display

Show skills as styled cards with name, description, and MP cost in the state panel:

```javascript
const skills = s.skills.map(sk =>
    `<div style="...">
      <div>${sk.name}</div>
      <div>${sk.desc}</div>
      <div>MP:${sk.mp}</div>
    </div>`
).join(' ');
```

For battle skill buttons, include MP cost in the text and use HTML `title` attribute for tooltip on hover.

## Modal UI Pattern

Backpack and shop use overlay modals. Each modal has its own HTML container:
```html
<div class="modal" id="backpack-modal">
  <div class="modal-box">
    <span class="modal-close" onclick="closeBackpack()">&times;</span>
    <div id="bp-list"></div>
  </div>
</div>
```

For shop: fetch `/api/shop-items` from the backend (NOT hardcoded frontend list) to ensure indices match.

## Pitfalls

1. **`=== true` fails for undefined** — Use truthy check (`if (conn)`) instead of `conn === true` for JSON booleans from optional API fields.
2. **Hardcoded shop item list desyncs** — Frontend and backend must use the same item list. Fetch from `/api/shop-items` endpoint.
3. **`input()` in API handler** — Never call terminal `input()` from an API handler. The thread blocks and the request hangs.
4. **Dungeon map connector index off-by-one** — Horizontal connectors per row = 4 (not 5). Formula: `idx = row*4 + col`, NOT `row*5 + col`.
5. **Start room can have enemy content** — After random start position generation, explicitly set `start_room.content = "empty"`.
6. **Browser cache** — Use `-H "Cache-Control: no-cache"` when testing via curl, or hard-refresh in browser (Ctrl+F5).
7. **Disabled buttons** — For dungeon directions that aren't available, show grayed-out buttons using a `.disabled` CSS class (not `disabled` attribute) to keep them in the DOM for layout.
8. **Missing closing `}` after edits** — When patching functions like `renderState()`, verify the closing brace still exists. A missing `}` causes all subsequent functions to be nested inside it, breaking the entire script.
9. **`html` variable undefined after refactor** — When adding fighting/enemy sub-sections to renderState, declare `let html = ...` at the top and only assign to `innerHTML` at the very end. Mixing inline `innerHTML =` with `html +=` causes ReferenceError.
10. **Enemy scaling tied to player level** — If monsters scale with player level, high-level players can't revisit early floors. Scale with dungeon floor instead and add reward degradation.
11. **Shop index mismatch** — Frontend hardcoded shop list (9 items) vs backend SHOP_ITEMS (10 items) have different indices. Always fetch `/api/shop-items` to ensure buy(index) matches backend.
12. **URL encoding for save_id** — Save IDs contain non-ASCII chars (Chinese). Use `encodeURIComponent()` in JS fetch calls, or test via API with proper URL encoding.
13. **Missing skill type handlers** — `re_mp` and `re_hp` skill types fall through to `else` in `player_turn()`, dealing damage instead of healing. Must handle explicitly with early return (no damage).
14. **`input()` in battle functions** — DO NOT reuse terminal `interactive_battle()` in web API. It calls `input()` and blocks. Implement step-based turn logic instead.
15. **Multi-hit skills need special handling** — `type: multi` skills iterate `hits` times and sum damage. Don't let them fall through to a single-hit calculation.
16. **Buff/debuff turn tracking** — When a buff has multi-turn duration (`turns: 3`), decrement `character.buff_turns` each turn and reset `character.buff = 1.0` when it reaches 0.
17. **Loot drop messages** — After battle victory with material drops, add a `gs.add_msg(f"📦 掉落 {mat_name}！")` so the player knows what dropped. Terminal version uses `print()`, web version needs explicit `add_msg()`.
18. **Shop item dynamic pricing** — When prices change based on purchase count (e.g., backpack expansion), compute the real-time price in the frontend using `STATE.backpack_max` and only use the backend's static `item.price` as a base. Display the dynamic price text to avoid confusion.

## References

- `references/session-example.md` — Full session trace of creating a web RPG from a terminal game
