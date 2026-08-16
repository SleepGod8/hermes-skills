---
name: hermes-mcp-configuration
description: "Add, remove, test, and troubleshoot MCP servers in Hermes Agent — stdio vs HTTP transports, non-interactive prompt automation, tool naming, ModelScope hosted MCP servers."
version: 1.0.0
author: agent
license: MIT
tags: [hermes, mcp, configuration, modelscope, tools]
---

# Hermes MCP Server Configuration

Add external capabilities (web fetch, filesystem, GitHub, databases) to Hermes via MCP servers. Covers the `hermes mcp` CLI, non-interactive automation, and hosted MCP servers (ModelScope etc.).

## When to Use

- User asks to add an MCP server (fetch, filesystem, github, etc.)
- User provides an `mcpServers` JSON config and wants it applied
- MCP tools don't appear in the current session
- Need to test whether a configured MCP server is reachable

## Core CLI

```bash
hermes mcp list             # show configured servers + tool counts + status
hermes mcp add NAME --url URL          # HTTP/streamable transport
hermes mcp add NAME --command "npx ..." # stdio transport
hermes mcp remove NAME      # remove a server
hermes mcp test NAME        # verify connection + tool discovery
hermes mcp configure NAME   # toggle which tools are enabled
```

## Non-Interactive Automation (interactive prompts)

`hermes mcp add` asks two interactive questions:
1. `Does this server require authentication? [Y/n]`
2. `Enable all N tools? [Y/n/select]`

**Pitfall**: These prompts hang the tool call (60s timeout) if run without a TTY. Answer both via piped input:

```bash
printf 'n\ny\n' | hermes mcp add fetch --url "https://..."
```

- `n` = no auth needed (or `y` if the server needs a token/header)
- `y` = enable all discovered tools
- If only one prompt answered (`printf 'n\n'`), the second prompt cancels the whole add — always answer both.

## Config Location & Format

Servers are stored in `config.yaml` under `mcp_servers:`:

```yaml
mcp_servers:
  fetch:
    url: https://mcp.api-inference.modelscope.net/<token>/mcp   # HTTP transport
    enabled: true
  # stdio variant:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_..."
    enabled: true
```

Verify the file path with `hermes config path` (on Windows: `C:\Users\<user>\AppData\Local\hermes\config.yaml`).

## Tool Naming & Activation

- Tools appear as `mcp_<server>_<tool>` (hyphens/dots → underscores)
- **New servers require a new session / `/reset`** — MCP tools are discovered at startup, no hot-reload
- Test first: `hermes mcp test NAME` → shows `✓ Connected`, transport, and discovered tools

## ModelScope Hosted MCP Servers

ModelScope (魔搭) hosts community MCP servers at `https://mcp.api-inference.modelscope.net/<token>/mcp` (streamable HTTP). Find servers at https://modelscope.cn/mcp/servers/. Each hosted server has its own token path — copy the full URL from the server page, don't guess.

**Verified example — Fetch** (`@modelcontextprotocol/fetch`, converts HTML → Markdown for LLM consumption):
```yaml
mcp_servers:
  fetch:
    url: https://mcp.api-inference.modelscope.net/2502ec5371944f/mcp
    enabled: true
```
Verification (2026-08): `hermes mcp test fetch` → `✓ Connected (10937ms)`, 1 tool discovered (`fetch`). No auth required.

## HTTP Auth (Bearer Token) MCP — Correct Setup

For remote HTTP MCP servers that need an `Authorization: Bearer <token>` header (e.g. official Hugging Face `https://huggingface.co/mcp`, verified 2026-08):

**The `--auth header` interactive flow is unreliable in PTY automation** — the `getpass` prompt for "API key / Bearer token" can read the token and then fail to persist it (config gets saved WITHOUT `headers:`, `.env` gets no `MCP_<NAME>_API_KEY`), and it can leave duplicate server entries. Do NOT rely on answering the token prompt.

**Correct recipe (verified):**

1. **Pre-seed the token into `.env`** (Hermes env path = `$(hermes config path)` dir's `.env`, i.e. `C:\Users\<user>\AppData\Local\hermes\.env`):
   ```bash
   echo "MCP_HUGGINGFACE_API_KEY=hf_..." >> "C:/Users/80704/AppData/Local/hermes/.env"
   ```
   Env key format is `MCP_<NAME>_API_KEY` (name uppercased, non-alphanumerics → `_`). The CLI reads this file and auto-detects it.

2. **Add the server WITHOUT `--auth`** (do not pass `--auth header`):
   ```bash
   hermes mcp add huggingface --url "https://huggingface.co/mcp"
   ```
   Answer the two interactive prompts (PTY + `process submit` works; piped `printf 'y\ny\n'` also works for the auth + enable questions):
   - `Does this server require authentication? [Y/n]` → `y`
   - CLI prints `✓ MCP_HUGGINGFACE_API_KEY: already configured` (means step 1 worked)
   - `Enable all N tools? [Y/n/select]` → `y`

3. **Verify the persisted config** — it must contain the header TEMPLATE (never the raw token in config.yaml):
   ```yaml
   mcp_servers:
     huggingface:
       url: https://huggingface.co/mcp
       headers:
         Authorization: Bearer ${MCP_HUGGINGFACE_API_KEY}
       enabled: true
   ```
   `hermes mcp test huggingface` → `✓ Connected`, tools discovered.

**Notes:**
- `--env` is ONLY for stdio servers; passing it with `--url` errors: "✗ --env is only supported for stdio MCP servers".
- `hermes config set env.MCP_X_API_KEY <token>` writes the raw token into config.yaml's top-level `env:` block (triggers "not a recognized config key" warning) — NOT the same as `.env`; avoid it. Clean up with `hermes config unset env.MCP_X_API_KEY` if used by accident.
- Duplicate entries: if a failed add left `hugging_face` + `huggingface` (name mangling), remove both with `hermes mcp remove NAME` then re-add.
- config.yaml is protected from direct patch/write_file — use `hermes config set/unset` for config keys, `hermes mcp remove` for servers, and direct `>>` append for `.env` only.

## Pitfalls

- **uvx stdio servers + PYTHONPATH contamination (Windows, verified 2026-08)**: running an MCP server via `uvx` from inside a Hermes session inherits Hermes's own venv on `PYTHONPATH`, so the server imports Hermes's `mcp`/pydantic instead of its own → cryptic ImportError. Fix: pass `--env PYTHONPATH=` (empty value) to `hermes mcp add`. Note `--env` MUST come BEFORE `--args` (args must be the last option, otherwise `--env PYTHONPATH=` gets swallowed into args and the config is broken — verified).
- **mcp-server-fetch version lock (`mcp==1.1.3`, verified 2026-08)**: upstream `mcp-server-fetch` (2026.7.10) declares `mcp>=1.1.3` with no upper bound; the newest mcp SDK renamed `McpError` → `MCPError`, so a bare `uvx mcp-server-fetch` crashes with `ImportError: cannot import name 'McpError' from 'mcp.shared.exceptions'`. Fix: `hermes mcp add fetch --command uvx --env PYTHONPATH= --args --from mcp-server-fetch --with mcp==1.1.3 mcp-server-fetch`. Manual smoke test: `printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"t","version":"1"}}}\n' | env PYTHONPATH= uvx --from mcp-server-fetch --with mcp==1.1.3 mcp-server-fetch` → expect a JSON `result` with `serverInfo.name: mcp-fetch`.
- **stdio frame format MUST be JSONL (mcp SDK ≥1.x)**: the official mcp Python SDK (`mcp/client/stdio`) reads/writes **one JSON per line, `\n`-separated**. A custom stdio server that speaks LSP-style `Content-Length:` framing will hang: `hermes mcp test` times out (~35s), tools never appear in new sessions, and the server's stderr stays empty (it's waiting for a frame the SDK never sends). Fix: `sys.stdout.buffer.write(json.dumps(payload) + b"\n")` and `json.loads(stdin.readline())`. Verified against mcp 1.28.1 (2026-08): after switching hermes-comfyui's server.py to JSONL, `mcp test` went from ✗ 35s timeout to ✓ 219ms and all 9 comfy_* tools loaded in a fresh session.
- **Interactive prompts hang in non-TTY tool calls**: `hermes mcp add` without piped stdin times out after 60s at the auth prompt. Always pipe `printf 'n\ny\n'`.
- **Partial pipe input cancels the add**: answering only the auth prompt (`printf 'n\n'`) leaves the "Enable all tools?" prompt unanswered → `Cancelled`. Answer both prompts.
- **Config key is `mcp_servers`, not `mcp` or `servers`** — wrong key silently disables MCP discovery.
- **HTTP servers need `url`, stdio servers need `command`** — a config with both or neither fails validation.
- **Bearer token missing after `--auth header` add**: if `hermes mcp list` shows the server but config.yaml has NO `headers:` block (or `.env` has no `MCP_<NAME>_API_KEY`), the interactive token prompt silently failed. Re-seed `.env` manually then re-add without `--auth` (see "HTTP Auth (Bearer Token) MCP — Correct Setup" section above).
- **`mcp` Python package required**: if startup logs show "MCP SDK not available -- skipping MCP tool discovery", install `pip install mcp` (or `uv pip install mcp`).
- **Tools missing after add**: check `hermes mcp list` shows the server enabled; if yes, start a new session (`/reset`) — MCP tools load at startup only.
- **HTTP import error**: "requires HTTP transport but mcp.client.streamable_http is not available" → `pip install --upgrade mcp`.

## Verification Checklist

1. `hermes mcp list` → new server present, `✓ enabled`
2. `hermes mcp test NAME` → `✓ Connected`, tool count matches expectation
3. New session → `mcp_<server>_*` tools available
4. Config file: `grep -A 3 "name:" $(hermes config path)` shows url/command + enabled
