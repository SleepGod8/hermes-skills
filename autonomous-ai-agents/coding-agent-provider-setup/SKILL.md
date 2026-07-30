---
name: coding-agent-provider-setup
description: "Configure external coding agent CLIs (Codex, Claude Code) with custom OpenAI-compatible API providers (proxies, local LLMs) — config structure, env var setup (Windows), and verification."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [Coding-Agent, Codex, Claude-Code, Custom-Providers, Proxy, China, ASLNet]
    related_skills: [codex, claude-code, hermes-custom-providers, opencode]
---

# Coding Agent Provider Setup

Configure external coding agent CLIs (Codex, Claude Code, OpenCode) to use
**custom OpenAI-compatible API endpoints** — third-party proxies (ASLNet,
ChatAnywhere), local LLM servers (Ollama, vLLM), or regional providers.
Essential when OpenAI itself is inaccessible (China users, regional blocks)
or when a specific model backend is needed.

## When to Use

- Primary OpenAI API is blocked/inaccessible in your region
- You want to use a proxy service for cost savings or model access
- You need to point a coding agent at a local LLM (Ollama, llama.cpp server)
- Switching between multiple providers for different tasks

## Common Provider Architecture

```
Coding Agent CLI (Codex / Claude Code / OpenCode)
        │
        ▼
  OpenAI-compatible API endpoint (proxy / local server)
        │
        ▼
  Underlying model (GPT, Claude, DeepSeek, Qwen, etc.)
```

The key insight: most coding agents accept an **OpenAI-compatible** endpoint,
so any API that speaks the OpenAI wire protocol can be used as a backend.

## Codex CLI

### Config Location
`~/.codex/config.toml` (TOML format)

### Provider Config Structure

```toml
model_provider = "myprovider"      # ← switch active provider here
model = "gpt-5.6-sol"

[model_providers.myprovider]
name = "myprovider"
base_url = "https://api.example.com"   # no /v1 suffix
wire_api = "responses"                   # "responses" or "chat_completions"
env_key = "MY_API_KEY"                   # env var for the API key
supports_websockets = false
```

| Field | Meaning |
|-------|---------|
| `base_url` | API root (Codex appends `/v1/responses` or `/v1/chat/completions`) |
| `wire_api` | `"responses"` (OpenAI Responses API) or `"chat_completions"` |
| `env_key` | Env var name to read for the API key |
| `supports_websockets` | Usually `false` for third-party proxies |

### Verification

```bash
codex doctor
```

Look for:
```
default model provider   myprovider
provider auth env var    MY_API_KEY (present)
myprovider API base URL  https://api.example.com reachable (HTTP 200)
myprovider API route probe ... route exists (HTTP 401)
```

HTTP 401 on the route probe is **normal** — auth is required.

## Setting API Keys on Windows

Set the env var in **three places** for full coverage:

```bash
# 1. Windows user environment (new cmd/PowerShell/any process)
setx YOUR_API_KEY "sk-..."

# 2. Git-bash login shells (new MINGW64 sessions)
echo 'export YOUR_API_KEY=sk-...' >> ~/.bashrc

# 3. Hermes .env (Hermes-managed agent sessions)
echo "YOUR_API_KEY=sk-..." >> ~/AppData/Local/hermes/.env
```

**Current session** also needs `export YOUR_API_KEY=sk-...` — `setx` only
affects new windows, not the current one.

## Wire API Discovery (curl)

Test if a proxy supports the Responses API (needed by Codex):

```bash
# Test Responses API
curl -s "https://api.example.com/v1/responses" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-5.5","input":"hi","max_output_tokens":10}'

# Fallback: Chat Completions API
curl -s "https://api.example.com/v1/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-5.5","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'

# List available models
curl -s "https://api.example.com/v1/models" \
  -H "Authorization: Bearer $API_KEY"
```

## Pitfalls

- **`base_url` without `/v1` suffix** — Codex appends it. Wrong: `.../v1`,
  Right: `https://api.example.com`
- **`setx` needs new terminal** — doesn't affect current session; always
  pair with `export` or `source ~/.bashrc`
- **Responses API not universal** — some proxies only support
  `chat_completions`. Test first, then set `wire_api` accordingly
- **`codex doctor` in Python subprocess** — Codex CLI may not be in Python's
  PATH; use `terminal()` directly
- **Config file is TOML** — not JSON. Strings use `"..."`, tables use
  `[section]` syntax, booleans are lowercase (`true`/`false`)

## Examples

See `references/aslnet-example.md` for a complete working example using
ASLNet (`https://api.aslnet.cloud`) with Codex CLI, including model list,
config fragment, env var setup, and curl verification commands.
