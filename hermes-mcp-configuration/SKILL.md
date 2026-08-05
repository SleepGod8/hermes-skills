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

## Pitfalls

- **Interactive prompts hang in non-TTY tool calls**: `hermes mcp add` without piped stdin times out after 60s at the auth prompt. Always pipe `printf 'n\ny\n'`.
- **Partial pipe input cancels the add**: answering only the auth prompt (`printf 'n\n'`) leaves the "Enable all tools?" prompt unanswered → `Cancelled`. Answer both prompts.
- **Config key is `mcp_servers`, not `mcp` or `servers`** — wrong key silently disables MCP discovery.
- **HTTP servers need `url`, stdio servers need `command`** — a config with both or neither fails validation.
- **`mcp` Python package required**: if startup logs show "MCP SDK not available -- skipping MCP tool discovery", install `pip install mcp` (or `uv pip install mcp`).
- **Tools missing after add**: check `hermes mcp list` shows the server enabled; if yes, start a new session (`/reset`) — MCP tools load at startup only.
- **HTTP import error**: "requires HTTP transport but mcp.client.streamable_http is not available" → `pip install --upgrade mcp`.

## Verification Checklist

1. `hermes mcp list` → new server present, `✓ enabled`
2. `hermes mcp test NAME` → `✓ Connected`, tool count matches expectation
3. New session → `mcp_<server>_*` tools available
4. Config file: `grep -A 3 "name:" $(hermes config path)` shows url/command + enabled
