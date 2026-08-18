---
name: coding-agent-anthropic-providers
description: "Configure Claude Code with third-party Anthropic endpoints."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [Coding-Agent, Claude-Code, Anthropic-Protocol, DeepSeek, Custom-Providers, Third-Party-Endpoints]
    related_skills: [coding-agent-provider-setup, claude-code, chinese-ai-providers, hermes-custom-providers]
---

# Coding Agent × Anthropic-Protocol Providers

Configure coding agent CLIs that speak the **Anthropic wire protocol** (`/v1/messages`,
`x-api-key` / `Authorization: Bearer`) — chiefly Claude Code — to run on third-party
endpoints instead of official Anthropic auth. Essential when the Anthropic account is
banned, has no subscription, or a specific backend (DeepSeek, proxy, local gateway) is wanted.

**Relationship to `coding-agent-provider-setup`**: that skill covers **OpenAI-compatible**
endpoints (Codex responses/chat_completions). This one covers **Anthropic-protocol**
endpoints. They are siblings; pick by wire protocol of the target CLI.

## Architecture

```
Claude Code CLI
      │  ANTHROPIC_BASE_URL + ANTHROPIC_AUTH_TOKEN
      ▼
Anthropic-protocol endpoint (https://api.deepseek.com/anthropic, proxy, LiteLLM)
      │
      ▼
Underlying model (deepseek-v4-pro, GLM, Qwen, local LLM…)
```

Claude Code reads its endpoint from `~/.claude/settings.json` → `env` (or env vars).
No `claude auth login` needed — the endpoint config replaces official OAuth entirely.

## 1. Install on Windows to a non-C drive (user preference: keep C clean)

```bash
mkdir -p /e/npm-global
npm config set prefix "E:\\npm-global"    # permanently move npm global install dir
npm install -g @anthropic-ai/claude-code
```

Persist PATH with PowerShell — **do NOT use setx** (1024-char truncation risk, and in
git-bash `$PATH` is MSYS-style and would be written corrupted):
```bash
powershell.exe -NoProfile -Command "[Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path','User') + ';E:\npm-global', 'User')"
```
Current session only: `export PATH="/e/npm-global:$PATH"`.

## 2. Endpoint config — ~/.claude/settings.json

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "<API_KEY>",
    "ANTHROPIC_MODEL": "deepseek-v4-pro",
    "API_TIMEOUT_MS": "300000",
    "CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT": "1"
  }
}
```

- Read the key from a secret store (e.g. Hermes `.env` `DEEPSEEK_API_KEY`); never hardcode
  it into docs/skills.
- `CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1` silences the third-party-model
  warning ("not a model this version recognizes") — unknown models default to a 200k
  assumed window.

## 3. DeepSeek model status (verified 2026-08)

`GET https://api.deepseek.com/models` (`Authorization: Bearer $KEY`) returns:
```
- deepseek-v4-flash   # lightweight — daily/Hermes use
- deepseek-v4-pro     # full model — coding (Claude Code should use this)
```
⚠️ **`deepseek-chat` (V3-era alias) has been REMOVED from /models**; the Anthropic
endpoint still accepts it during a compatibility window, but new configs must not use it.

## 4. Verification — three steps (never trust claude's self-report alone)

1. **List models**: `curl -s https://api.deepseek.com/models -H "Authorization: Bearer $KEY"`
2. **Endpoint reachability**: use **Python urllib, not curl with Chinese body** — in
   git-bash, `curl -d '{"content":"中文"}'` fails with `invalid unicode code point`
   (JSON body mangled by the shell — a shell issue, not a model issue):
   ```python
   import json, urllib.request
   req = urllib.request.Request("https://api.deepseek.com/anthropic/v1/messages",
       data=json.dumps({"model":"deepseek-v4-pro","max_tokens":32,
           "messages":[{"role":"user","content":"Reply OK"}]}).encode(),
       headers={"x-api-key": KEY, "anthropic-version":"2023-06-01",
                "content-type":"application/json"})
   # HTTP 200 + content[].text = pass
   ```
3. **End-to-end**: `claude -p "用一句话回答你是谁" --max-turns 1` — confirm the reply is
   driven by the configured model.

## 5. Accepting Claude Code output (mandatory)

`claude -p` summaries are **self-reports**. Verify: ① `ls`/read the artifact to confirm
it exists ② actually run it (interactive programs: `printf 'input\n' | python x.py`)
③ check the exit code. Instance: guess-number game `guess_game.py` (3004 bytes, piped
input ran the full flow, exit 0).

## 6. ASLNet as an Anthropic endpoint (verified 2026-08-18)

ASLNet (`https://api.aslnet.cloud`) — the user's GPT-series proxy — speaks the
Anthropic wire protocol directly. Verified end-to-end with Claude Code:

- **`https://api.aslnet.cloud/v1/messages`** ✅ works (both `x-api-key` and
  `Authorization: Bearer`, non-stream AND SSE `stream:true`, HTTP 200).
- **`https://api.aslnet.cloud/anthropic/v1/messages`** ❌ returns an HTML page
  (404 frontend) — do NOT append `/anthropic`. Unlike DeepSeek's layout, the
  path segment is not needed.
- **`ANTHROPIC_BASE_URL` = `https://api.aslnet.cloud`** (no `/v1` — Claude Code
  appends `/v1/messages` itself).

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.aslnet.cloud",
    "ANTHROPIC_AUTH_TOKEN": "<ASLNET_API_KEY from Hermes .env>",
    "ANTHROPIC_MODEL": "gpt-5.5",
    "API_TIMEOUT_MS": "300000",
    "CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT": "1"
  }
}
```

- Models verified on this endpoint: `gpt-5.5` (stable default), `gpt-5.6-sol`
  (strongest reasoning), `gpt-5.6-terra`, `gpt-5.4` (cheaper) — same pool as
  Codex/ASLNet.
- `[claude-code:unrecognized_model]` log noise is harmless — the unknown-model
  window-enforcement disable flag lets gpt-5.5 run anyway.
- Probe before switching (key lives in `~/AppData/Local/hermes/.env`):
  ```bash
  curl -s -m 60 "https://api.aslnet.cloud/v1/messages" \
    -H "Authorization: Bearer $KEY" -H "anthropic-version: 2023-06-01" \
    -H "Content-Type: application/json" \
    -d '{"model":"gpt-5.5","max_tokens":20,"messages":[{"role":"user","content":"say ok"}]}'
  ```
  Expect `"type":"message"`; then end-to-end `claude -p "reply with exactly: ASLNet OK" --max-turns 1`.
- Always back up `settings.json` before editing (DeepSeek config archived at
  `settings.json.bak-20260818-1529`; restore = copy back, then restart claude).

⚠️ **Trade-off to state to the user**: ASLNet's gpt-5.x is OpenAI-family — far
stricter moderation than DeepSeek. If zero-censorship was the point of the
delegation, keep DeepSeek; ASLNet is fine for ordinary coding work.

## Pitfalls

- `claude` not found in a new terminal → user PATH not refreshed; export in the current
  session first.
- `claude auth login` is pointless when the account is banned — go straight to the
  endpoint config.
- `claude auth status` may report `loggedIn:true / oauth_token` (OAuth residue) — judge
  by an actual `claude -p` call.
- Multi-profile sync: batch-copy SKILL.md with Python file ops into
  `profiles/*/skills/...`, append rules to each `memories/MEMORY.md` (`§` separator,
  Windows `\r\n` line endings, dedupe before append).

## Multi-agent convention (this user's family)

Coding tasks in multi-agent development are delegated to Claude Code (`claude -p`);
Hermes/maids handle requirement-splitting, acceptance, reporting.

Claude Code config is **user-global** — every Hermes profile shares the single
`~/.claude/settings.json`; there is NO per-profile isolation (a project-level
`.claude/settings.local.json` is the only per-directory override). Current
endpoint (2026-08): ASLNet gpt-5.5 (see §6). DeepSeek config archived at
`~/.claude/settings.json.bak-20260818-1529` — restore by copying back.
