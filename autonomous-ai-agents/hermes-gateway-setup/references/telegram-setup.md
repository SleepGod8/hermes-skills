# Telegram Gateway Setup Reference

## Prerequisites

1. **Bot Token** from [@BotFather](https://t.me/BotFather)
2. **User ID** from [@userinfobot](https://t.me/userinfobot)
3. **Proxy** (if Telegram API is blocked in your region)

## Interactive Setup Sequence

The wizard has a sub-menu for Telegram that requires these piped inputs:

```
22          # Platform number for Telegram
2           # Manual mode (vs Automatic/QR)
<bot_token> # Paste the token
<user_id>   # Your numeric user ID
            # Enter to finish
```

Full command:
```bash
echo -e "22\n2\n8633020924:AAER9Zmo...\n6552494345\n\n" | hermes gateway setup
```

## Manual Config (Env Vars)

Add to `~/.hermes/.env`:
```bash
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=8633020924:AAER9Zmo-Wj3nJw7HUG6--ZyUvBpkVIhkvE
TELEGRAM_ALLOWED_USERS=6552494345
```

Add to `~/.hermes/config.yaml` (via `hermes config set`):
```bash
hermes config set platforms.telegram.enabled true
```

## Proxy (Required in China)

```bash
# HTTP proxy
echo "TELEGRAM_PROXY=http://127.0.0.1:7890" >> ~/.hermes/.env

# SOCKS5 proxy
echo "TELEGRAM_PROXY=socks5://127.0.0.1:1080" >> ~/.hermes/.env

# Or in config.yaml:
hermes config set telegram.proxy_url socks5://127.0.0.1:1080
```

## Gateway Restart Workaround

`hermes gateway restart/stop` is **blocked** from within the gateway:
```bash
# 1. Find PID
hermes gateway status
# 2. Kill externally
taskkill -F -PID <PID>
# 3. Start fresh
hermes gateway start
```

## Verification

```bash
# Check logs for connection status
grep -E "telegram|connected|running with" "C:\Users\Windows\AppData\Local\hermes/logs/gateway.log"

# Expected output:
# [Telegram] Connecting to Telegram (attempt 1/8)…
# ✓ telegram connected
# Gateway running with 2 platform(s)
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `api.telegram.org connection failed` | Network blocked (GFW) | Configure proxy |
| `TELEGRAM_BOT_TOKEN not found` | Env var not set | Add TELEGRAM_ENABLED=true + TELEGRAM_BOT_TOKEN |
| `Gateway running with 1 platform(s)` only | Telegram not picked up | Check TELEGRAM_ENABLED=true, restart |
| `Unauthorized user` | User ID not in allowlist | Add to TELEGRAM_ALLOWED_USERS or approve via `hermes pairing approve telegram <id>` |
