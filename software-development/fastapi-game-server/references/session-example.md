# Session Reference: Land of Heroes Web Frontend

Full session implementing a web frontend for a terminal RPG at D:\PythonProject\Land of Heroes.

## Project Structure After Refactoring

```
Land of Heroes/
├── run.py                          # Entry: python run.py
├── server.py                       # FastAPI web server (port 8080)
├── saves.json                      # Save file (auto-created)
├── land_of_heroes/
│   ├── __init__.py
│   ├── data.py                     # Constants: SKILL_DATA, SHOP_ITEMS, TREASURE_LOOT
│   ├── character.py                # Main_character class
│   ├── items.py                    # use_item, equip_item, try_add_item, backpack_menu
│   ├── battle.py                   # Monster, EliteMonster, interactive_battle (terminal)
│   ├── dungeon.py                  # DungeonRoom, Dungeon (5x5 procedural)
│   ├── locations.py                # Location, MainCity, Wilderness, Map
│   └── main.py                     # create_character, main_loop (terminal)
└── static/
    └── index.html                  # Web frontend (SPA, single file)
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| State in memory (not DB) | Single-player game, restarts on server restart. Simpler than SQLite. |
| Full state returned per API call | Frontend is a pure renderer — no client-side game logic |
| Save as JSON file | Portable, human-readable, no database needed |
| Skill data name-based lookup | SKILL_DATA dict indexed by occupation name string |
| Random dungeon start position | More variety; start room forced to "empty" to avoid instant battle |
| Both-explored path display | Changed from "either explored" after user feedback — spoils exploration |
| Shop via API | Frontend fetches shop items; avoids hardcoded list desync |
| 4 direction buttons always shown | Fixed order ↑↓←→ with disabled styling; user can see what's unavailable |

## Save File Format

```json
{
  "saves": [{
    "id": "勇者_战士",
    "name": "勇者", "occupation": "战士",
    "level": 3, "exp": 250,
    "hp": 180, "max_hp": 200,
    "mp": 35, "max_mp": 45,
    "attack": 35, "spell_power": 5,
    "gold": 120, "backpack_max": 10,
    "backpack": [{"name": "生命药水", "count": 3, ...}],
    "equipment": {"weapon": {"name": "铁剑", ...}, "offhand": null, ...},
    "saved_at": "2026-07-24 10:00"
  }]
}
```

## Monster Scaling Formula

```python
# Monster stat scaling:
s = 1 + (player_level - 1) * 0.5
self.hp = int(random.randint(20, 35) * s)
self.attack = int(random.randint(4, 8) * s)
```

## Dungeon Connection Indices (critical for rendering)

- conn_h: 20 items. For row ry (0-4), col rx (0-3): idx = ry*4 + rx
- conn_v: 20 items. For col rx (0-4), row ry (0-3): idx = ry*5 + rx
- Only show paths when BOTH adjacent rooms are explored.
