#!/usr/bin/env python3
"""Gateway health checker — restarts Hermes gateway if unresponsive (event loop stall).
Watchdog pattern: empty stdout when healthy (silent), prints notice only when action taken.
Place at %HERMES_HOME%\\scripts\\ and run via a Windows Scheduled Task every N minutes:
  schtasks /create /tn "Hermes Gateway Watchdog" /tr "python C:\\Users\\<user>\\AppData\\Local\\hermes\\scripts\\gateway-health-check.py" /sc minute /mo 5 /f
"""
import subprocess
import sys
import os
from datetime import datetime

HERMES = os.path.expandvars(
    r"C:\Users\80704\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe"
)

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 1) Gateway responsive? (timeout = stalled event loop)
try:
    result = subprocess.run(
        [HERMES, "gateway", "status"],
        capture_output=True, text=True, timeout=10
    )
    if "running" in result.stdout.lower():
        sys.exit(0)  # healthy — stay silent
    print(f"[{now()}] Gateway not running — attempting restart...")
except subprocess.TimeoutExpired:
    print(f"[{now()}] Gateway unresponsive (timeout) — restarting...")
except Exception as e:
    print(f"[{now()}] Check failed: {e} — restarting...")

# 2) Kill the bloated stuck process (tune MEMUSAGE to observed size)
try:
    subprocess.run(
        ["taskkill", "/F", "/FI", "IMAGENAME eq hermes.exe", "/FI", "MEMUSAGE gt 300000"],
        capture_output=True, timeout=10
    )
except Exception:
    pass

# 3) Restart with --replace (bypasses stale lock)
try:
    subprocess.run(
        [HERMES, "gateway", "run", "--replace"],
        capture_output=True, timeout=15
    )
    print(f"[{now()}] Gateway restart initiated.")
except subprocess.TimeoutExpired:
    print(f"[{now()}] Gateway restart initiated.")
except Exception as e:
    print(f"[{now()}] Restart failed: {e}")
    sys.exit(1)
