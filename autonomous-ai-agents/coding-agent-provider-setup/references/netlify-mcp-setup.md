# Netlify MCP Server for Codex CLI

Configure Codex to deploy sites to Netlify via the official `@netlify/mcp`
package instead of the OpenAI plugin catalog (which requires ChatGPT auth).

## Setup

```bash
# Install the Netlify MCP server
npm install -g @netlify/mcp
```

## Config

Add to `~/.codex/config.toml`:

```toml
[mcp_servers.netlify]
command = "node"
args = ["C:\\Users\\Windows\\AppData\\Local\\hermes\\node\\node_modules\\@netlify\\mcp\\dist\\netlify-mcp.js"]
startup_timeout_sec = 30
```

**Do NOT** add a `[mcp_servers.netlify.env]` section — Codex does not support
`${VAR}` interpolation in MCP env blocks. Instead, set `NETLIFY_AUTH_TOKEN` as
a system-level env var:

```bash
setx NETLIFY_AUTH_TOKEN "nfp_yourtoken"          # Windows
export NETLIFY_AUTH_TOKEN="nfp_yourtoken"         # current session
```

## Token

1. Visit https://app.netlify.com/user/applications/personal
2. Create a **Personal Access Token**
3. Set `NETLIFY_AUTH_TOKEN` env var (see above)

## Verification

Confirm the MCP server starts and responds:

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' \
  | node "C:\\Users\\Windows\\AppData\\Local\\hermes\\node\\node_modules\\@netlify\\mcp\\dist\\netlify-mcp.js" \
  | head -1
```

Expected response:
```json
{"result":{"protocolVersion":"2024-11-05","capabilities":{"tools":{"listChanged":true}},"serverInfo":{"name":"netlify-mcp","version":"1.15.1"}},"jsonrpc":"2.0","id":1}
```

Then run `codex doctor` — look for:
```
✓ mcp  2 server (2 stdio) · 0 disabled
```

## Troubleshooting

### MCP section has orphaned keys

If the `[mcp_servers.netlify]` section contains unrelated settings like
`BROWSER_USE_AVAILABLE_BACKENDS` or `NODE_REPL_TRUSTED_CODE_PATHS`, the
TOML section boundaries got corrupted (common when using `patch` tool near
section headers). Fix by removing those orphaned lines — they belong under
`[shell_environment_policy.set]` or `[mcp_servers.node_repl.env]`.

### codex doctor shows "MCP optional issues"

Run `codex doctor` and check for `⚠ mcp  MCP configuration has optional issues`.
This usually means the `[mcp_servers.netlify]` section has invalid keys.
Read the full config and validate with Python:
```bash
python -c "import tomllib; f=open(r'C:\Users\Windows\.codex\config.toml','rb'); tomllib.load(f); print('Valid TOML'); f.close()"
```
