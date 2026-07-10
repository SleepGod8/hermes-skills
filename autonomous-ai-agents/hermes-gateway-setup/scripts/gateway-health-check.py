#!/usr/bin/env python3
"""Gateway health checker — restarts if unresponsive (event loop stall).
Designed for Windows schtasks watchdog: runs every N minutes.
Only outputs to stdout when action is taken (silent-when-healthy pattern).
Exit 0 = gateway OK (silent). Exit 1 = restart attempted.
"""
import subprocess
import sys
import os
from datetime import datetime

HERMES = os.path.expandvars(
    r"%LOCALAPPDATA%\hermes\hermes-agent\venv\Scripts\hermes.exe"
)

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 1) Check if gateway responds within 10s
try:
    result = subprocess.run(
        [HERMES, "gateway", "status"],
        capture_output=True, text=True, timeout=10
    )
    if "running" in result.stdout.lower():
        # Gateway is responsive, all good — silent exit
        sys.exit(0)
    else:
        print(f"[{now()}] Gateway not running — attempting restart...")
except subprocess.TimeoutExpired:
    print(f"[{now()}] Gateway unresponsive (timeout) — restarting...")
except Exception as e:
    print(f"[{now()}] Check failed: {e} — restarting...")

# 2) Kill any stuck hermes gateway processes (>300MB memory is suspicious)
try:
    subprocess.run(
        ["taskkill", "/F", "/FI", "IMAGENAME eq hermes.exe",
         "/FI", "MEMUSAGE gt 300000"],
        capture_output=True, timeout=10
    )
except Exception:
    pass

# 3) Start gateway with --replace (bypasses stale lock file)
try:
    subprocess.run(
        [HERMES, "gateway", "run", "--replace"],
        capture_output=True, timeout=15
    )
    print(f"[{now()}] Gateway restarted successfully.")
except subprocess.TimeoutExpired:
    # gateway run is a long-running process, timeout is expected
    print(f"[{now()}] Gateway restart initiated.")
except Exception as e:
    print(f"[{now()}] Restart failed: {e}")
    sys.exit(1)
