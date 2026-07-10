---
name: hermes-custom-providers
description: "Configure custom AI providers in Hermes via OpenAI-compatible endpoints — for providers not natively in Hermes's resolution chains (vision, compression, etc.)."
version: 1.0.0
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
```

### Step 3: Verify

The `hermes config show` output should show the custom provider under Auxiliary Models.

## Pitfalls

- **`hermes config set custom_providers "..."` overwrites the entire list.** Use direct YAML editing via Python for multi-entry lists, or always include all existing entries.
- **Not all providers are in Hermes's native vision resolution chain.** Check `agent/auxiliary_client.py` in the Hermes source — the vision chain is: main provider (if supported) → OpenRouter → Nous Portal → Anthropic → custom endpoint. DashScope, Kimi, and most Chinese providers are NOT in the native chain; they MUST be configured as custom providers.
- **Model name format**: use the same model name the provider's own API expects (e.g., `qwen-vl-max` for DashScope, not `dashscope/qwen-vl-max`).
- **Content filtering**: Chinese providers (DashScope, etc.) enforce content restrictions. For uncensored vision, prefer Google Gemini Flash (free tier, `GOOGLE_API_KEY`).

## DashScope (阿里云百炼) Quick Reference

See `references/dashscope.md` for endpoint URLs, model names, and known issues.
