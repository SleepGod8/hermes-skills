# Hermes Desktop Gateway Startup Troubleshooting

## Common Failure: "Hermes couldn't start — Timed out connecting to Hermes backend after 15000ms"

### Root Causes

1. **Stale lock file** — Gateway process died but `gateway.lock` still exists, blocking restart
2. **Slow platform startup** — Telegram/WhatsApp retry loops delay Gateway readiness beyond Desktop's 15s timeout
3. **Manual Gateway conflict** — Running `hermes gateway run` in terminal conflicts with Desktop's built-in Gateway

### Recovery Steps

#### Quick Fix (90% of cases)

```bash
# Kill all Hermes processes
taskkill /F /IM Hermes.exe

# Then open Desktop — let it start its own Gateway automatically
```

**Do NOT run `hermes gateway run` manually before opening Desktop.** Desktop manages its own Gateway instance.

#### If Desktop Still Fails: Disable Unnecessary Platforms

After a fresh Windows boot, Telegram DNS resolution can take 30-60s, exceeding Desktop's timeout:

```bash
# Disable slow platforms
hermes config set platforms.telegram.enabled false
hermes config set platforms.whatsapp.enabled false
```

Or in `.env`:
```
TELEGRAM_ENABLED=false
WHATSAPP_ENABLED=false
```

(Telegram's `enabled` flag lives in `config.yaml`, not `.env` — use `hermes config set`)

#### Stale Lock File Recovery

When `taskkill /F /IM Hermes.exe` doesn't clear the lock:

```bash
# The --replace flag bypasses stale locks
hermes gateway run --replace
```

After Gateway starts cleanly, Desktop's "Retry" button should work.

### Verification

Check Gateway state:
```bash
cat ~/AppData/Local/hermes/gateway_state.json
```

Look for `"gateway_state": "running"` and platform states.

### Prevention

- After Windows reboot, Desktop's Gateway will NOT auto-start. Simply open Desktop — it handles startup internally.
- Avoid running `hermes gateway run` in terminal on the same machine as Desktop.
- Consider disabling unused messaging platforms permanently to speed up startup.
