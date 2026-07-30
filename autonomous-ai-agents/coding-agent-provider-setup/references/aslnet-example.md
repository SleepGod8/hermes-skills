# ASLNet — Codex CLI Provider Example

ASLNet (`https://api.aslnet.cloud`) is an OpenAI-compatible API proxy that
supports both Chat Completions and Responses API formats. This makes it a
suitable backend for Codex CLI's `wire_api = "responses"` mode.

## Available Models

| Model | Tier | Use Case |
|-------|------|----------|
| gpt-5.6-sol | 🏆 Flagship | Default for Codex |
| gpt-5.6-luna | High | Complex reasoning |
| gpt-5.6-terra | Balanced | General coding |
| gpt-5.6 | Standard | General coding |
| gpt-5.5 | Stable | Reliable baseline |
| gpt-5.4 | Light | Quick lookups |
| gpt-5.4-mini | Budget | Simple tasks |
| codex-auto-review | Specialized | PR review automation |

## Config Fragment

```toml
model_provider = "aslnet"
model = "gpt-5.6-sol"

[model_providers.aslnet]
name = "aslnet"
base_url = "https://api.aslnet.cloud"
wire_api = "responses"
env_key = "ASLNET_API_KEY"
supports_websockets = false
```

## Env Var

```
ASLNET_API_KEY=sk-3d69f24097c128ec54eff1fc5d454d567f4358986d42d4dc35178196fcba10bb
```

## Verification Commands

```bash
# 1. Check models
curl -s "https://api.aslnet.cloud/v1/models" \
  -H "Authorization: Bearer $ASLNET_API_KEY" | jq '.data[].id'

# 2. Test chat completions
curl -s "https://api.aslnet.cloud/v1/chat/completions" \
  -H "Authorization: Bearer $ASLNET_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-5.5","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'

# 3. Test responses API (Codex wire format)
curl -s "https://api.aslnet.cloud/v1/responses" \
  -H "Authorization: Bearer $ASLNET_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-5.5","input":"hi","max_output_tokens":10}'

# 4. Full doctor check
ASLNET_API_KEY=$ASLNET_API_KEY codex doctor
```
