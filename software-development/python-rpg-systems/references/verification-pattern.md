# Ad-hoc Verification Pattern

Used extensively during RPG development to verify each system before moving on.

## File naming
```
C:/Users/Windows/AppData/Local/Temp/hermes-verify-{system-name}.py
```

## Template
```python
"""Ad-hoc verification: {system name}"""
import sys, os
sys.path.insert(0, 'D:/PythonProject/Land of Heroes')
# For monolithic: exec(open('land_of_heroes.py').read().split("if __name__")[0])
# For package: from land_of_heroes.character import Main_character  (explicit imports)

errors = []

# Test 1: ...
# Test 2: ...

if errors:
    print("❌ 验证失败:")
    for e in errors: print(f"  • {e}")
    sys.exit(1)
else:
    print(f"✅ 所有验证通过！")
    print(f"   ① result1")
    print(f"   ② result2")
```

## Running
```bash
python "C:/Users/Windows/AppData/Local/Temp/hermes-verify-X.py"
```

## Cleanup
```bash
rm -f "C:/Users/Windows/AppData/Local/Temp/hermes-verify-*.py"
```

## Mocking stdin for interactive functions
```python
import io, sys
sys.stdin = io.StringIO('0\n')  # simulate player choosing option 0
result = interactive_battle(character, monster)
```

## What to verify
- **Math**: EXP formula correctness, overflow handling
- **State**: HP/MP changes after rest, items removed after use
- **Boundaries**: Backpack full, insufficient MP, level cap
- **Probability**: Run distributions (e.g., 1000 iterations) to verify rare events fire
- **Edge cases**: Monster at 1 HP, player at 1 HP, empty backpack
