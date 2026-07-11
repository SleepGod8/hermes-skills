# Hermes Desktop Connectivity Troubleshooting

## The Core Issue

Hermes Desktop (the native Electron app) has its own **built-in gateway manager**. It starts, monitors, and manages the gateway process internally. When you manually run `hermes gateway run` alongside it, the two compete for the same resources (ports, lock files, state) and neither works properly.

## Decision Flow

```
Desktop shows "Timed out connecting to Hermes backend after 15000ms"
│
├─ Is `hermes gateway run` currently running in a terminal?
│  YES → Ctrl+C it, then taskkill /F /IM Hermes.exe, then open Desktop
│  NO  → Continue below
│
├─ Are there zombie Hermes processes?
│  Check: tasklist | findstr Hermes
│  YES → taskkill /F /IM Hermes.exe, then open Desktop
│  NO  → Continue below
│
├─ Does gateway startup log show platforms retrying (Telegram 1/8...)?
│  YES → Gateway is starting too slow. Disable unused platforms.
│        hermes config set platforms.telegram.enabled false
│        Add WHATSAPP_ENABLED=false to .env
│        Then taskkill /F /IM Hermes.exe, open Desktop
│  NO  → Try "Repair install" button in Desktop
│
└─ Still failing?
   → Check gateway logs: cat ~/AppData/Local/hermes/logs/gateway.log | tail -50
   → Run hermes doctor
   → Try Repair install
```

## Key Distinction

| Scenario | Fix |
|----------|-----|
| Standalone gateway crash/stall | `hermes gateway run --replace` |
| Desktop app can't connect | Kill all Hermes.exe, let Desktop auto-start |
| Slow platform connections | Disable unused platforms in config |

**Never use `hermes gateway run --replace` when the Desktop app is the one that will be connecting** — Desktop doesn't look for a manually-started gateway; it starts its own.

## Verifying the Fix

After applying the fix:
1. Open Desktop — it should show the main window without error
2. Check the WeChat/Weixin icon shows "connected"
3. Send a test message from WeChat to confirm the channel works
4. The terminal should NOT show `hermes gateway run` — Desktop manages this invisibly

## Why This Happens After Reboot

Desktop on Windows doesn't auto-start its gateway service after a system reboot. The gateway process from the previous session may leave behind stale lock files (`gateway.lock`, `gateway.pid`). When Desktop tries to start fresh, it hits the lock and times out waiting for a process that doesn't exist.

The fix (kill all + let Desktop restart) handles both the zombie state and the fresh start in one shot.
