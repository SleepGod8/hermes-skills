---
name: hermes-troubleshooting
description: "Troubleshoot Hermes Agent — Desktop connectivity, gateway stalls, platform startup issues, stale lock files. Quick-reference recovery patterns for common failure modes."
version: 1.0.0
author: agent
license: MIT
tags: [hermes, troubleshooting, desktop, gateway, recovery]
---

# Hermes Troubleshooting

Quick recovery patterns for common Hermes failure modes. Each scenario has a distinct root cause and fix — don't mix them up.

## Scenario 1: Desktop "Timed out connecting to Hermes backend after 15000ms"

**Symptom**: Desktop app shows "Hermes couldn't start" with the timeout error. Gateway may or may not be running separately.

**Root cause**: Desktop has its own **built-in gateway manager**. Manually running `hermes gateway run` creates a competing process that prevents Desktop from binding to its expected port/socket.

**Fix**:
```bash
# 1. Kill ALL Hermes processes
taskkill /F /IM Hermes.exe

# 2. Do NOT run `hermes gateway run` manually
# 3. Just open the Desktop app — it will auto-start its own gateway
```

**DO NOT** run `hermes gateway run --replace` for this scenario — that creates the conflict that causes the timeout.

## Scenario 2: Gateway event loop stalled (微信通道卡死)

**Symptom**: WeChat/Weixin channel stops responding, `hermes` commands time out, `gateway.log` shows "event loop stalled".

**Fix**:
```bash
# 1. Find and kill the largest Hermes process
taskkill /F /PID <pid_of_largest_hermes>

# 2. Restart with --replace to bypass stale lock
hermes gateway run --replace
```

## Scenario 3: Slow gateway startup causes Desktop timeout

**Symptom**: Desktop times out waiting for gateway, gateway terminal shows platforms retrying (e.g. Telegram 1/8, 2/8...).

**Root cause**: Unused platforms (Telegram, WhatsApp) trying to connect on networks where they're blocked, delaying the "ready" signal past Desktop's 15s timeout.

**Fix — disable slow platforms**:
```bash
# Telegram: config.yaml (NOT just .env)
hermes config set platforms.telegram.enabled false

# WhatsApp: .env
printf 'WHATSAPP_ENABLED=false\n' >> ~/AppData/Local/hermes/.env
```
Then restart: kill all Hermes.exe, open Desktop.

## Scenario 4: Stale lock file blocks gateway

**Symptom**: Gateway won't start, lock file references a dead PID.

**Fix**:
```bash
hermes gateway run --replace
```
`--replace` bypasses the stale lock check and starts fresh.

## Platform-specific: PowerShell Pitfalls

On Windows machines that default to PowerShell:
- `echo "text" >> file` writes the **quotes** into the file — use `printf` instead
- `grep` doesn't exist — use `Select-String -Path <file> -Pattern "<pattern>"`
- `~` works in PowerShell paths but prefer `$env:USERPROFILE`

## References

- `references/desktop-connectivity.md` — detailed Desktop app connectivity troubleshooting
