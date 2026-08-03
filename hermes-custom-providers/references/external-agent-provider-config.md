# Configuring Custom Providers for External Coding Agents

Same Chinese proxy services (ASLNet, ChatAnywhere etc.) that work for Hermes
can power external coding agents like **Codex CLI**, **Claude Code**, and
**OpenCode**. Each has its own config mechanism.

## Codex CLI

Codex reads `~/.codex/config.toml`. Add a `[model_providers.<name>]` section:

```toml
model_provider = "aslnet"
model = "gpt-5.6-sol"

[model_providers.aslnet]
name = "aslnet"
base_url = "https://api.aslnet.cloud"     # no /v1 suffix
wire_api = "responses"                     # or "chat_completions"
env_key = "ASLNET_API_KEY"                 # env var name, not the key itself
supports_websockets = false
```

### Wire API: Responses vs Chat Completions

Codex prefers the **Responses API** (`wire_api = "responses"`). Test if your
proxy supports it:

```bash
curl -s "https://your-proxy/v1/responses" \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-5.5","input":"hi","max_output_tokens":10}'
```

- Returns JSON with `"object":"response"` → Responses API supported
- Returns 404 / HTML / error → fall back to `wire_api = "chat_completions"`

### Env Var Setup (Two Places)

```bash
# ~/.bashrc — interactive terminal sessions
export ASLNET_API_KEY="sk-your-key-here"

# ~/AppData/Local/hermes/.env — Hermes-managed sessions
ASLNET_API_KEY=sk-your-key-here
```

On Windows, also run `setx ASLNET_API_KEY "sk-..."` so cmd/PowerShell and
non-bash processes (e.g. the Codex desktop app, MCP servers) see it. `setx`
only affects NEW terminals — export in the current session too. Missing env
var surfaces as `Missing environment variable: ASLNET_API_KEY`.

### Verification

```bash
ASLNET_API_KEY=$ASLNET_API_KEY codex doctor | grep -E "default model|env var|reachable|HTTP"
# Expect: default model provider = <name>, env var (present), reachable (HTTP 200)
```

### ASLNet Models (Verified Working with Codex)

| Model | Notes |
|-------|-------|
| `gpt-5.6-sol` | Best for complex tasks |
| `gpt-5.6-luna` | Strong alternative |
| `gpt-5.6-terra` | Balanced |
| `gpt-5.6` | Standard |
| `gpt-5.5` | Stable, well-tested |
| `gpt-5.4` / `gpt-5.4-mini` | Lightweight |
| `codex-auto-review` | Code review mode |

## Claude Code

Claude Code uses `ANTHROPIC_API_KEY` (for official Anthropic API) or the
`ANTHROPIC_BASE_URL` env var for custom endpoints. Not all proxies support
Anthropic's Message API format — test with:

```bash
curl -s "https://your-proxy/v1/messages" \
  -H "x-api-key: $KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-sonnet-4","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
```

## OpenCode

OpenCode reads `OPENAI_API_KEY` and `OPENAI_BASE_URL` env vars. Set both:

```bash
export OPENAI_API_KEY="sk-your-proxy-key"
export OPENAI_BASE_URL="https://your-proxy/v1"
opencode exec "do something"
```

## Universal Pitfalls

1. **Proxy must support the specific API format** the agent uses. Codex
   prefers Responses API, Claude uses Messages API, OpenCode uses Chat
   Completions. One proxy may not support all three.
2. **Env var not found in non-login shells**: `bashrc` only applies to
   interactive login shells. For Hermes terminal sessions, set vars in
   `~/AppData/Local/hermes/.env` or pass inline.
3. **Region-locked accounts**: OpenRouter blocks Chinese accounts from
   OpenAI/Anthropic/Google models. Proxies bypass this because they have
   their own API keys — your key goes to the proxy, not to OpenRouter.
4. **Rate limits differ**: Proxies may have tighter rate limits than the
   original provider. Start with simple tasks and ramp up.

## Codex remote_plugin vs MCP Servers (2026-07 verified)

Switching Codex to a third-party provider triggers a startup error:
`list remote plugin catalog: chatgpt authentication required for remote plugin catalog`.
That comes from the `remote_plugin` feature (stable) trying to fetch OpenAI's
plugin catalog without ChatGPT auth.

- `codex features disable remote_plugin` → clean startup, but **`codex plugin list` only shows locally cached/bundled plugins** — you cannot search/install new plugins from OpenAI's catalog.
- Keep `remote_plugin = true` if the user needs the catalog; the warning is non-fatal.
- **Plugin missing → install an MCP server instead.** Most "plugins" wrap CLI/API capabilities. Example: Netlify plugin was not in the local catalog, so install the official MCP server:

```bash
npm install -g @netlify/mcp
```

```toml
# ~/.codex/config.toml
[mcp_servers.netlify]
command = "node"
args = ["C:\\Users\\<user>\\AppData\\Local\\hermes\\node\\node_modules\\@netlify\\mcp\\dist\\netlify-mcp.js"]
startup_timeout_sec = 30
```

- **Do NOT use `${VAR}` interpolation in `[mcp_servers.X.env]`** — Codex does not expand it and `codex doctor` reports `MCP configuration has optional issues`. Drop the env block and let the server inherit the system env var (setx'd token works).
- Verify: `codex doctor` shows `✓ mcp N server (N stdio) · 0 disabled`. Probe a stdio server directly by piping an initialize JSON-RPC to its stdin — expect `serverInfo.name` back.

## Codex Desktop (Windows AppX) identification

- `codex` in PATH may be the npm CLI (`codex-cli X.Y.Z`), while the **desktop GUI is a separate AppX package** `OpenAI.Codex` — it runs `app/ChatGPT.exe` and the desktop shortcut is named `ChatGPT.lnk`, not `Codex.lnk`. Don't tell the user "Codex isn't installed" based on the shortcut name.
- `codex app` printing `Codex Desktop not found; opening Windows installer...` ≠ desktop uninstalled; it means the CLI can't locate the AppX.
- AppX status: `powershell Get-AppxPackage *Codex*` → InstallLocation under `C:\Program Files\WindowsApps\OpenAI.Codex_...`.
- Desktop logs: `C:\Users\<user>\AppData\Local\Packages\OpenAI.Codex_<hash>\LocalCache\Local\Codex\Logs\<YYYY>\<MM>\<DD>\`. Healthy marker: `install-primary-runtime ... problemCount=0`; `401 Unauthorized` warnings are normal without ChatGPT login.

## config.toml edit accidents (important)

Patching `~/.codex/config.toml` with fuzzy replace can swallow following
top-level keys into the matched `[section]` (observed: three
`[shell_environment_policy.set]` keys got merged into `[mcp_servers.netlify]`),
which silently breaks the desktop app ("click icon, nothing happens").

After ANY config.toml edit, verify:

```bash
python -c "import tomllib; tomllib.load(open(r'C:\Users\<user>\.codex\config.toml','rb')); print('TOML OK')"
codex doctor
```

Re-read the whole file before re-patching (especially when the tool warns the
file was modified externally).
