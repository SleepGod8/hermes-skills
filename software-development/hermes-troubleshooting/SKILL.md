---
name: hermes-troubleshooting
description: "Troubleshoot Hermes Agent — Desktop connectivity, gateway stalls, platform startup issues, stale lock files. Quick-reference recovery patterns for common failure modes."
version: 1.2.0
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

## Scenario 5: One computer works, another doesn't (多台电脑)

**Symptom**: Hermes Desktop works fine on computer A, but computer B shows "Timed out connecting to Hermes backend after 15000ms" even after following Scenario 1.

**Root cause**: Each computer has independent state. Computer B may have different platforms enabled, a stale lock file, or different network conditions.

**Fix** — run on the broken computer:
```bash
# Kill all Hermes processes
taskkill /F /IM Hermes.exe

# Disable slow/unused platforms
hermes config set platforms.telegram.enabled false
printf 'WHATSAPP_ENABLED=false\n' >> ~/AppData/Local/hermes/.env

# Open Desktop — let it auto-start
```

**Verify** Gateway came up:
```bash
cat ~/AppData/Local/hermes/gateway_state.json
# Look for "gateway_state": "running"
```

## Scenario 6: Hermes fails to initialize with httpx/openai import error

**Symptom**: Hermes Desktop or Gateway crashes on startup with an error like:
```
Failed to initialize OpenAI client: cannot import name 'URL' from 'httpx' (unknown location)
```
or any `ImportError` mentioning `httpx` and `openai` together.

**Root cause**: `httpx` 0.28+ removed the `URL` class that older `openai` packages depend on. Hermes Desktop bundles its own Python with these packages, and a version mismatch can occur after auto-updates or fresh installs when the bundled `httpx` is too new for the bundled `openai`.

**Fix — Option A: Pin httpx in Hermes's bundled Python** (precise):

```bash
# 1. Find Hermes's bundled Python (typical locations):
#    C:\Users\<用户名>\AppData\Local\hermes\python\python.exe
#    or inside the Hermes Desktop install directory.

# 2. Pin httpx to the compatible version:
"C:\Users\<用户名>\AppData\Local\hermes\python\python.exe" -m pip install httpx==0.27.2
```

**Fix — Option B: Reinstall/update Hermes Desktop** (simpler):

1. Download the latest Hermes Desktop installer
2. Install over the existing installation (no need to uninstall first)
3. Restart Hermes Desktop — the latest build should have compatible packages

**Fix — Option C: Upgrade openai instead** (if you can access the bundled pip):

```bash
"C:\Users\<用户名>\AppData\Local\hermes\python\python.exe" -m pip install --upgrade openai
```

**Note**: This is a Python package-level error, NOT a connectivity or gateway issue. `taskkill` and `--replace` won't help — the packages themselves need fixing.

## Scenario 7: QQ Bot gateway won't connect or receive messages

**Symptom**: QQ gateway configured but not loading (`Gateway running with 1 platform(s)`), or connected but receiving no messages.

**Quick checklist**:
1. Config key is `qqbot` (NOT `qq`)
2. Credentials go under `extra.app_id` / `extra.client_secret` (NOT top-level)
3. `is_reconnect` parameter may need adding to adapter (v0.18.2)
4. Bot must be **published** on q.qq.com, not sandbox
5. User must add bot as QQ friend before messaging

See `references/qq-gateway.md` for full setup and debugging guide.

## References

- `references/desktop-connectivity.md` — detailed Desktop app connectivity troubleshooting
- `references/httpx-openai-conflict.md` — httpx/openai version conflict details
- `references/qq-gateway.md` — QQ Bot gateway setup, config format, pairing, and debugging
