# Land of Heroes（勇者大陆）— Reference Implementation

A terminal-based RPG built in Python with 7 modules across 729 lines.

## File map

```
Land of Heroes/
├── run.py                          # Entry: `python run.py`
└── land_of_heroes/
    ├── __init__.py                 # Empty package marker
    ├── data.py                     # Constants (78 lines)
    ├── character.py               # Main_character class (61 lines)
    ├── items.py                    # item/equip/backpack functions (137 lines)
    ├── battle.py                   # Monster, battle, escape, death (137 lines)
    ├── dungeon.py                  # 5×5 procedural dungeon (150 lines)
    ├── locations.py               # MainCity, Wilderness, Map (133 lines)
    └── main.py                     # create_character, main_loop (64 lines)
```

## Key design decisions

| Decision | Why |
|----------|-----|
| `data.py` has zero internal imports | Avoids circular deps; every other module imports from it |
| `character.py` only imports from `data` | No circular risk; `items.py` imports `character` for `Main_character` references |
| Backpack stores `{item, count}` not flat items | Enables per-category stacking (consumables=5, materials=10, equipment=1) |
| Dungeon connections via union-find | Guarantees all 25 rooms reachable (100% connectivity) |
| Death penalty via `_respawn` flag | Clean separation: battle sets flag, main loop reads it at while-top |
| Exit room content NEVER set to "empty" | Players can return to exit and still access next floor |
| WASD with mapped arrow labels | `moves['d'] = (nx, ny, '→')` — input = WASD, display = arrows |

## Monster scaling formula

```
scale = 1 + (player_level - 1) * 0.5
hp = randint(20, 35) * scale
attack = randint(4, 8) * scale
exp = round(100 * 1.5^(level-1) * uniform(0.15, 0.25))
gold = level * randint(1, 2)  # reduced after sell system added
```

## EXP geometric progression

```
Lv1→2: 100
Lv2→3: 150
Lv3→4: 225
Lv4→5: 337  (round, not int — int would give 337, round gives 338)
Lv5→6: 506
```

## Equipment slots

| Key | Chinese | Purpose |
|-----|---------|---------|
| `weapon` | 武器 | Attack bonus |
| `offhand` | 副手 | HP/Spell bonus |
| `armor` | 防具 | HP/Spell bonus |
| `accessory` | 饰品 | Attack/HP bonus |

## Skill types

| type | Effect | Example |
|------|--------|---------|
| `dmg` | `attack * mult` or `spell_power * mult` | 猛击(1.5x), 陨石术(3.5x) |
| `multi` | `attack * mult` × hits | 连射(1.5x × 2) |
| `buff` | Set `character.buff` for this turn | 铁壁(50%减伤) |
| `re_mp` | Restore `max_mp * pct` | 法力涌动(30%) |
| `re_hp` | Restore `max_hp * pct` | 治愈术(25%) |
