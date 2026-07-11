---
name: android-emulator-automation
description: "Automate Android games on PC emulators (MuMu, BlueStacks) via ADB + OpenCV template matching — screenshot, click, and loop."
version: 1.0.0
author: agent
license: MIT
platforms: [windows]
category: gaming
---

# Android Emulator Game Automation

Automate repetitive tasks in Android games running on PC emulators (MuMu,
BlueStacks, etc.) using ADB for device control and OpenCV for visual
template matching.

## When to Use

- User wants to automate grinding / farming in a mobile game on an emulator
- User asks for a "script" or "bot" for a specific mobile game
- User mentions MuMu, BlueStacks, Nox, LDPlayer + "auto" or "script"

## Quick Start

```bash
# Install deps
pip install opencv-python pillow numpy

# Run the template script (copy from templates/wc4_conquest.py)
python wc4_conquest.py
```

## Architecture

```
┌─────────────┐     ADB      ┌──────────────┐     OpenCV      ┌──────────┐
│  Python      │ ──click────→ │  Emulator     │ ──screenshot─→ │  Script   │
│  Script      │ ←──screen── │  (MuMu etc.)  │                │  Logic    │
└─────────────┘              └──────────────┘                └──────────┘
```

## MuMu Emulator ADB Setup

MuMu 12 uses a different ADB port than older versions:

| Version | Default ADB Port |
|---------|-----------------|
| MuMu 6  | `7555` |
| MuMu 12 | `16384` or `21503` |

Find the port: MuMu → Settings → Network → ADB port.

Enable ADB: MuMu → Settings → Other → "Enable ADB debugging" must be ON.

Connect:
```bash
adb connect 127.0.0.1:16384
adb devices  # verify
```

## Template Matching Workflow

1. Screenshot via ADB:
   ```python
   adb("shell screencap -p /sdcard/screen.png")
   ```

2. Match template:
   ```python
   result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
   ```

3. Click center of match:
   ```python
   adb(f"shell input tap {center_x} {center_y}")
   ```

## Script Modes (see templates/wc4_conquest.py)

| Mode | When to Use |
|------|------------|
| **Coordinate-based** (mode 1) | Quick test, known fixed button positions |
| **Template-matching** (mode 2) | Long-term automation, UI may shift |
| **Coordinate recorder** (mode 3) | Initial setup: find and record button positions |

## Pitfalls

1. **ADB path**: On Windows, `adb` may not be in PATH. Either install Android SDK
   Platform Tools or find MuMu's built-in adb at `MuMuPlayer-12.0/shell/adb.exe`.

2. **Python environment**: Hermes venv has no pip. Use system Python
   (`C:\Users\<user>\AppData\Local\Python\pythoncore-3.14-64\python`) or install
   deps globally.

3. **Template resolution**: Templates must match the emulator's resolution
   exactly. Different emulator window sizes need new templates.

4. **Game-specific logic**: Each game needs its own strategy (produce units,
   move, attack). The script provides a framework — game logic is in the
   `conquest_loop()` / `simple_conquest_loop()` functions.

5. **Timing**: Always add `time.sleep()` between actions. ADB commands are
   fast; the game UI needs time to animate.

## WC4 Conquest Mode Template

The `templates/wc4_conquest.py` file is a ready-to-customize script for
World Conqueror 4 conquest mode auto-expansion. Copy it and modify:

- `ADB_HOST` — your emulator's ADB port
- City coordinates in `simple_conquest_loop()`
- Template images in `templates/` folder
- Production priorities in `produce_unit()`
