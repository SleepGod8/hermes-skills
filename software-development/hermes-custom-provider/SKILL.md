---
name: hermes-custom-provider
description: "Add any OpenAI-compatible API provider (Agnes AI, custom endpoints, etc.) to Hermes Agent via hermes auth + config."
version: 1.0.0
author: Hermes Agent
tags: [hermes, provider, configuration, api-key, custom-endpoint]
---

# Hermes Custom Provider Setup

Add any OpenAI-compatible API provider to Hermes using credential pools and config.

## Recipe

```bash
# 1. Add API key to credential pool
echo "" | hermes auth add custom:<name> --type api-key --api-key "sk-..."

# 2. Set provider, base URL, and default model
hermes config set model.provider "custom:<name>"
hermes config set model.base_url "https://<api-host>/v1"
hermes config set model.default "<model-id>"

# 3. Verify
hermes config show | grep -A3 Model
```

## Switching back to a previous provider

```bash
hermes config set model.provider deepseek
hermes config set model.base_url "https://api.deepseek.com"
hermes config set model.default "deepseek-v4-pro"
```

## Adding MULTIPLE providers without changing the active model

`hermes config set model.provider ...` overwrites the active model. If you want to ADD
several providers into the pool while KEEPING the current active model, you have two options:

### Option A: JSON array via CLI (recommended for simplicity)

Re-set the entire `custom_providers` list with the new provider appended:

```bash
hermes config set custom_providers '[
  {"name": "deepseek", "base_url": "https://api.deepseek.com", "api_key": "sk-...70ad"},
  {"name": "glm", "base_url": "https://open.bigmodel.cn/api/paas/v4", "api_key": "df40...Zu"},
  {"name": "sharedchat", "base_url": "https://new.sharedchat.cc/codex", "api_key": "sk-d81...35a"}
]'
```

**Warning:** This replaces the entire `custom_providers` list — you must include ALL existing providers, not just the new one. Read the current list from config.yaml first if unsure.

### Option B: Python YAML editing

```python
import yaml
CFG = r"C:\Users\Windows\AppData\Local\hermes\config.yaml"
data = yaml.safe_load(open(CFG, encoding="utf-8"))
cps = data.setdefault("custom_providers", [])
cps.append({"name": "deepseek", "base_url": "https://api.deepseek.com", "api_key": "<key>"})
cps.append({"name": "glm", "base_url": "https://open.bigmodel.cn/api/paas/v4", "api_key": "<key>"})
yaml.safe_dump(data, open(CFG, "w", encoding="utf-8"), allow_unicode=True)
```

Notes:
- Pull the keys from `~/.hermes/.env` (e.g. `DEEPSEEK_API_KEY`, `GLM_API_KEY`) — never type
  them into chat. Check a var is non-empty with `grep -E "^VAR=" .env` then `cut -d= -f2-`,
  and validate length only (do NOT print raw secret values).
- After editing, re-parse with `yaml.safe_load` to confirm the file is still valid before
  reporting success.
- The pool does NOT include built-in providers like `openrouter`; they live under
  `model.provider`, not `custom_providers`.

## Pitfalls

- **Don't replace the provider config without saving the old values.** `hermes config set` overwrites. If you have multiple providers, keep the switch commands handy.
- **`hermes auth add` prompts for a label** — pipe empty string to accept default.
- **API key is auto-redacted in logs/output**, but the raw value is visible during config commands.
- **The provider format is `custom:<name>`** — this is how Hermes's agent router recognizes it as a custom endpoint rather than a built-in provider.
- ⚠️ **`custom:<name>` DOES NOT work for providers that have built-in support.** If you set `model.provider: custom:glm` for GLM/Zhipu AI, Hermes will silently reject it on new sessions with `Warning: Unknown provider 'custom:glm'. Falling back to auto provider detection.` — the session then uses OpenRouter (or whatever auto-detection finds) instead of GLM. **Use the built-in provider instead:**
  ```bash
  # GLM/Zhipu AI — use built-in 'zai' provider
  # Set GLM_API_KEY in .env, then:
  hermes config set model.provider zai
  hermes config set model.default "GLM-4.1V-Thinking-Flash"
  ```
  The `hermes model` command is your diagnostic tool — if it says "Unknown provider" for your `custom:`, that's the sign to switch to the built-in equivalent.
- **Provider/model changes require a new session** (`/new` or restart the CLI) to take effect. The `/model` slash command can switch the model name mid-session, but changing `model.provider` is a config-level change that only loads at startup.
- **Test the endpoint with curl first** before configuring in Hermes, to verify the key and base URL are correct:
  ```bash
  curl -s "https://<api-host>/v1/chat/completions" \
    -H "Authorization: Bearer sk-..." \
    -H "Content-Type: application/json" \
    -d '{"model":"<model-id>","messages":[{"role":"user","content":"hi"}],"max_tokens":50}'
  ```
- **OpenCode CLI (v1.17.20) does NOT support custom OpenAI-compatible base URLs.** Its built-in `openai` provider ignores `OPENAI_BASE_URL` and uses its own hardcoded endpoint. You can save the API key to its `auth.json`, but OpenCode won't route through a custom endpoint. Hermes does support custom endpoints — use it directly.
- **API base URL discovery**: when the platform's frontend is a Next.js SPA with no visible API docs, check the developer documentation section (look for `/doc/` paths on the main domain), probe common subdomain patterns (`api.<domain>.com`, `apihub.<domain>.com`) with curl, or inspect the browser's URL bar after navigating to the platform's API keys page.
- **Cloudflare 403 blocking the endpoint**: Some custom providers (especially free/shared services like SharedChat) sit behind Cloudflare with aggressive WAF rules. If you get `Access blocked by Cloudflare. This usually happens when connecting from a restricted region (status 403 Forbidden)`:
  - **Switch your proxy/VPN exit node** — the current IP may be blacklisted by Cloudflare. Try a different region/country.
  - **Check if the provider applied region restrictions** — some providers only allow USA/EU IPs. Test with a clean residential IP.
  - **The provider may have changed or deprecated the endpoint** — test with a direct curl from a clean IP to confirm.
  - **Cloudflare WAF with JS challenge**: API calls can't pass JS challenges. If the provider's website loads fine in a browser but API calls return 403, they may have enabled JS challenge on just the API routes. Contact the provider.
  - **Fallback**: if repeatedly blocked, switch to a known-working provider (deepseek, openrouter) rather than troubleshooting indefinitely. Report the issue to the provider's support.

## Silent verification workflow (recommended)

After adding a provider, always PROVE the key + base_url + model name actually work — don't trust the config alone. Use `scripts/verify_provider.py` for a ready-made, `.env`-backed silent probe (it never prints secrets).

- **Keys usually already exist in Hermes `.env`** under stable names: `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`, `GLM_API_KEY`, `AGNES_API_KEY`, `OPENROUTER_API_KEY`, etc. Read them in Python, never echo into chat.
- **Probe model-name validity with a real request**: HTTP `404` = wrong model name; HTTP `429` = name is VALID but the endpoint is currently overloaded. Do NOT conclude a model name is wrong from a 429 — it means "correct name, try later". (Seen live: `GLM-4.6V-Flash` returned 429 "访问量过大" but the name was correct; `GLM-4.1V-Thinking-Flash` returned 200.)
- **Thinking models** (e.g. Zhipu `GLM-4.1V-Thinking-Flash`) emit a ` ` … ` ` block then a ` ` answer. If you cap `max_tokens` too low (e.g. 60) the response truncates mid-` ` with `finish_reason:"length"` and looks "broken" — that is YOUR test limit, not the model. Use a larger cap (e.g. 400) to confirm a clean `finish_reason:"stop"`.
- **Re-verify before switching the active model to a new name**: if the probe shows 429, keep the config but warn the user the endpoint is overloaded; don't claim the model is unusable.

## Real-world example: Agnes AI

Provider: `custom:agnes`  
Base URL: `https://apihub.agnes-ai.com/v1`  
Model: `agnes-2.0-flash`  
Pricing: Free ($0/1M tokens), 512K context

Discovery process for finding the API base URL when the platform frontend is a Next.js SPA:
1. Check the official website for "Developer Docs" or "API" links
2. Look for `/doc/` or `/docs/` paths on the main domain
3. The API base URL may differ from the web app domain (e.g. `apihub.xxx.com` vs `platform.xxx.com`)
4. Test candidate URLs with curl before configuring
