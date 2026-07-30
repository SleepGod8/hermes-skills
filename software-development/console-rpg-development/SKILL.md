---
name: console-rpg-development
title: Console RPG Development
description: Build interactive Python console RPGs with class hierarchy, menu-driven UI, equipment, skills, backpack, shop, and battle systems.
---

# Console RPG Development

Build interactive single-player RPGs running in the terminal.

## Core Architecture

```
Location (base) → MainCity, Wilderness
Main_character (player state)
Map (location registry)
```

### Pattern: Feature → Implement → Verify
1. Receive feature spec (often prefixed with "以游戏设计师的身份")
2. Read current code state first
3. Design: data model → classes → game loop integration
4. Implement with patches or full file rewrite
5. Verify with ad-hoc `python -c` script (no pytest)
6. Clean up tmp verification files

## Design Patterns

### Location-based Actions
```python
LOCATION_ACTIONS = {
    MainCity: [("④","休息","补满HP/MP"), ("⑤","锻炼","+10经验"), ("⑥","商店","购买道具")],
    Wilderness: [("④","探索","战斗/宝箱")],
}
# Universal: ①状态 ②地图 ③移动 ⑦背包 ⑧退出
```

### Equipment System
- 4 slots: `weapon`, `offhand`, `armor`, `accessory`
- Each slot holds one item; equipping new puts old in backpack
- Class restrictions: `"classes": ["战士","骑士"]` or `None` (all)
- `apply_effect(character, field, val, add=True)` to toggle bonuses

### Skill System
```python
SKILL_DATA = {
    '职业': [
        {"name":"技能名","lv":1,"mp":0,"desc":"描述","type":"dmg","mult":1.5},
        {"name":"技能名","lv":5,"mp":10,"desc":"描述","type":"buff","def_mult":0.5},
    ]
}
```
- Types: `dmg`, `multi`, `buff`, `re_mp`, `re_hp`
- Skills gated by `lv`; optional `use_sp=True` for spell-based dmg

### Backpack with Stacking
- Backpack: `list[{"item": item_dict, "count": int}]`
- Consumables stack to `STACK_MAX=5`; equipment always `count=1`
- `try_add_item()` finds partial stacks first
- Full backpack → prompt: discard or abandon
- Discard from stack → ask quantity or "a" for all

### Economy
- `character.gold`; shop buy → backpack; monster kills drop small gold; treasure chests drop medium gold

### Battle System
- Turn-based: choose normal attack or skill; monster counters
- `character.buff` (default 1.0) reduces incoming dmg
- Win → EXP + gold; Lose → HP=1, no reward

## Item Data Format
```python
{"name":"物品名","desc":"描述","price":N,"effect":("field",val),
 "cat":"消耗品|装备|特殊",
 "slot":"weapon|offhand|armor|accessory",   # equipment only
 "classes":["战士","法师"] or None}
```

## Verification
```python
exec(open('game.py').read().split('if __name__')[0])
c = Main_character('t','职业')
assert ...; print('✅')
```
Use ad-hoc `python -c` scripts; clean up temps with `rm -f`.
