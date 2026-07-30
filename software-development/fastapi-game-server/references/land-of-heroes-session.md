# Land of Heroes — Session Notes

Full-stack web RPG built from a terminal Python game.

## Project Structure

```
D:/PythonProject/Land of Heroes/
├── server.py                     # FastAPI backend (game state, battle, dungeon, save/load)
├── run.py                        # Terminal entry point
├── saves.json                    # Save file (auto-created)
├── land_of_heroes/
│   ├── __init__.py
│   ├── data.py                   # Constants: skills, shop items, materials
│   ├── character.py              # Main_character class (stats, leveling)
│   ├── items.py                  # Item/equipment/backpack functions
│   ├── battle.py                 # Monster, EliteMonster, battle logic
│   ├── dungeon.py                # DungeonRoom, Dungeon (5x5 grid generation)
│   ├── locations.py              # MainCity, Wilderness, Map
│   └── main.py                   # Terminal game loop
└── static/
    └── index.html                # SPA frontend (HTML + CSS + JS)
```

## Key Design Decisions (settled by user feedback)

1. **Dungeon map paths**: Only show connections between rooms where BOTH are explored. No spoilers.
2. **Direction buttons**: Always show all 4 ↑↓←→, gray out unavailable ones.
3. **Exit room**: Show all movement buttons PLUS next-floor / return options simultaneously.
4. **Shop**: Fetch item list from backend `/api/shop-items`, don't hardcode in frontend.
5. **Save/Load**: Save ID = `{name}_{occupation}`. Same ID overwrites. Load creates new session.
6. **Enemy scaling**: By dungeon floor, not player level. Reward degradation for high-level players in low floors.
7. **Start room**: Must be explicitly set to "empty" content after random start position selection.
8. **Return to home**: A button that clears session and goes back to character select screen.

## Frontend Architecture

- Single `index.html` (~23KB) with embedded CSS (~350 lines) and JS (~1500 lines)
- Dark fantasy theme: `#0a0a12` background, `#e8c87a` gold accents, `#8ab8e0` skill blue
- State management: Global `STATE` object updated from every API response, `render()` redraws all panels
- Event handling: `data-act` / `data-payload` attributes on buttons, targeted with `querySelectorAll`
- Modal pattern: overlay div with `.show` class toggle, content injected via innerHTML

## Battle Flow (API-based)

1. Player moves → `POST /api/action/{sid}` with `{action: "dungeon_move", payload:{key:"d"}}`
2. If room has enemy → server creates `Monster(floor_level)`, sets `fighting: true`
3. Frontend shows enemy HP bar + attack buttons
4. Player clicks attack → `POST /api/action/{sid}` with `{action: "battle_attack", payload:{skill:-1}}`
5. Server: player_turn → if victory: rewards (with reward_mult degradation), clear enemy. Else: monster_turn → if death: clear inventory, respawn at main city.
6. Frontend re-renders with updated state

## Starting the Server

```bash
cd "D:/PythonProject/Land of Heroes"
python server.py
# → http://127.0.0.1:8080
```

## Bug History (notable fixes)

- `dungeon_move` called `interactive_battle` with `input()` — blocked thread. Replaced with step-based battle.
- Shop button created new game session instead of opening shop UI. Replaced with modal + API.
- Dungeon map connector index used `row*5+col` instead of `row*4+col` — off-by-one for horizontal connections.
- `renderState()` missing closing `}` after fighting code was added — all subsequent functions were nested inside it.
- Enemy created with `player_level` instead of `floor_level` — couldn't balance difficulty.
