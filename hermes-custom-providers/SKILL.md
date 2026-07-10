---
name: hermes-custom-providers
description: "Configure custom AI providers in Hermes via OpenAI-compatible endpoints — for providers not natively in Hermes's resolution chains (vision, compression, etc.)."
version: 1.3.0
author: agent
license: MIT
tags: [hermes, configuration, custom-providers, vision, china-providers]
---

# Hermes Custom Providers

When a provider is supported for chat but NOT in Hermes's auxiliary resolution chains (vision, compression, etc.), configure it as a **custom provider** with its OpenAI-compatible endpoint.

## When to Use

- Provider works for chat but auxiliary tasks (vision/compression) fail with "model not found"
- Provider doesn't appear in `auxiliary_client.py` vision/compression resolution chains
- You need to use a regional/Chinese provider (DashScope, Kimi, MiniMax, GLM) for vision

## How It Works

Hermes resolves custom providers via `custom:<name>` — the name matches a `custom_providers` entry in `config.yaml`. The key insight: most providers expose an **OpenAI-compatible** endpoint that Hermes can use transparently.

## Configuration Pattern

### Step 1: Add to custom_providers in config.yaml

```yaml
custom_providers:
  - name: YourProviderName
    base_url: https://api.example.com/compatible-mode/v1
    api_key: ${YOUR_API_KEY_ENV_VAR}
```

The `api_key` can reference an env var with `${VAR_NAME}` syntax, or be a raw key.

### Step 2: Set auxiliary task to use it

```bash
hermes config set auxiliary.vision.provider "custom:YourProviderName"
hermes config set auxiliary.vision.model "your-vision-model-name"
# For DashScope vision, use qwen-vl-plus (NOT qwen-vl-max — it rejects NSFW content)
```

### Step 3: Verify

The `hermes config show` output should show the custom provider under Auxiliary Models.

## Troubleshooting: 404 "model not found"

When vision fails with this exact error:
```
Model 'qwen-vl-max' not found. The requested model does not exist in our configuration or OpenRouter catalog.
```
…it means the provider is NOT in Hermes's native vision resolution chain. The fix is always: configure as a custom provider.

**Diagnostic checklist** (in order):
1. `hermes config show | grep Vision` → confirm provider/model are set correctly
2. `grep DASHSCOPE_API_KEY ~/AppData/Local/hermes/.env` → confirm API key exists
3. If provider is `dashscope` (bare, no `custom:` prefix) → **this is the bug**. Hermes doesn't know dashscope for vision. Switch to `custom:DashScope`.
4. Read `agent/auxiliary_client.py` (in `$HERMES_HOME/hermes-agent/agent/`) lines 17-23 to confirm the vision resolution chain: main provider → OpenRouter → Nous Portal → Anthropic → custom endpoint. Your provider must appear here or be a custom endpoint.
5. After fixing, restart gateway (`hermes gateway run --replace`) to pick up config changes.

## Pitfalls

- **`hermes config set custom_providers "..."` is DANGEROUS.** It has two failure modes:
  1. **Overwrites the entire list** — all existing custom providers are lost.
  2. **Serializes as a JSON string** — the CLI wraps the array value in quotes, producing broken YAML: `custom_providers: '[{...}]'`. Hermes won't parse this correctly.
  
  **Recovery**: use Python to manually merge entries (see `references/dashscope.md` for the repair script).
- **Not all providers are in Hermes's native vision resolution chain.** The chain in `agent/auxiliary_client.py` is: main provider (if supported) → OpenRouter → Nous Portal → Anthropic → custom endpoint. DashScope, Kimi, and most Chinese providers are NOT in the native chain; they MUST be configured as custom providers (`custom:<name>`, not just `<name>`).
- **Direct provider name won't work for vision**: Setting `auxiliary.vision.provider = dashscope` (without `custom:` prefix) silently fails — Hermes falls back to OpenRouter with a 404 "model not found" error. Always use `custom:DashScope`.
- **Model name format**: use the same model name the provider's own API expects (e.g., `qwen-vl-plus` for DashScope, not `dashscope/qwen-vl-plus`).
- **Content filtering varies by model**: `qwen-vl-max` enforces strict content restrictions (refuses NSFW/adult content). `qwen-vl-plus` does NOT — it describes anime/illustration content without filtering. Test both for your use case before falling back to Google Gemini (which requires a proxy from China).

## DashScope (阿里云百炼) Quick Reference

See `references/dashscope.md` for endpoint URLs, model names, and known issues.
