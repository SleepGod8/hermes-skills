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
- **`remote_plugin` feature triggers auth errors with third-party providers**
  — Codex tries to fetch OpenAI's remote plugin catalog on startup.
  If using a third-party provider (ASLNet, Ollama, etc.) and ChatGPT auth
  is unavailable, Codex logs `chatgpt authentication required for remote
  plugin catalog`. Disable remote plugin fetching:
  ```bash
  codex features disable remote_plugin
  ```
  This keeps local plugins (browser, pdf, documents, etc.) working fine;
  only the remote catalog search is suppressed.
- **Plugins unavailable → use MCP servers instead** — Without remote plugin
  catalog access, tools like Netlify deploy or Slack integration are
  unavailable as plugins. Workaround: install the tool's official MCP server
  and configure it as a Codex `[mcp_servers]` entry in `config.toml`:
  ```toml
  [mcp_servers.servicename]
  command = "node"
  args = ["path/to/mcp-server.js"]
  startup_timeout_sec = 30
  ```
  
  MCP servers use **stdio protocol** — verify with a JSON-RPC initialize call:
  ```bash
  echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' \
    | node /path/to/mcp-server.js | head -1
  ```
  
  This pattern works for any MCP-compatible tool and doesn't require OpenAI
  auth. See `references/netlify-mcp-setup.md` for a complete Netlify example.

- **TOML section corruption via `patch` tool** — The `patch` tool's fuzzy
  matching can merge adjacent `[section]` headers when the matched context
  includes nearby section boundaries. This produces orphaned keys under the
  wrong section. After editing `config.toml`, always validate:
  ```bash
  python -c "import tomllib; f=open('$CODEX_HOME/config.toml','rb'); tomllib.load(f); print('Valid TOML'); f.close()"
  ```
  If validation fails, read the full file and look for orphaned keys — lines
  that belong under one section but appear under another. The fix is to insert
  the dropped `[section.header]` before them.

- **MCP `[env]` block `${VAR}` syntax not supported** — Codex passes
  `${NETLIFY_AUTH_TOKEN}` as a literal string, not an env var reference.
  Set the env var at the system level (`setx`, `~/.bashrc`, or Hermes `.env`)
  and omit the `[mcp_servers.<name>.env]` subsection entirely.

## Codex Desktop "打不开" (won't open) — debugging path

When the Codex **Desktop** app (as opposed to the CLI) won't open after
config edits, don't assume the app is broken — walk this path:

1. **Desktop runs as `ChatGPT.exe`** on Windows. The AppX package is
   `OpenAI.Codex_2p2nqsd0c76g0` (find with
   `powershell.exe -Command "Get-AppxPackage *Codex*"`). A running
   `ChatGPT.exe` process (~500MB) means the Desktop IS running — the user may
   just be looking for the wrong shortcut (desktop shortcut is named
   `ChatGPT.lnk`, not `Codex.lnk`).
2. **`codex app` from the npm CLI can't find the AppX install** — the two are
   separate release channels (CLI `0.144.x` vs AppX `26.x.y`). The AppX
   executable lives under `C:\Program Files\WindowsApps\...` which is
   **permission-protected**; you cannot launch it directly from a shell.
   Launch via Start Menu / desktop shortcut instead.
3. **The usual real cause after config edits: a corrupted `config.toml`**.
   Validate it:
   ```bash
   python -c "import tomllib; f=open(r'C:\Users\Windows\.codex\config.toml','rb'); tomllib.load(f); print('Valid TOML'); f.close()"
   ```
   If invalid, check for orphaned keys (patch-tool fuzzy merge moved lines
   across `[section]` boundaries — see TOML pitfall above).
4. **Desktop logs** live in the AppX package:
   `C:\Users\Windows\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\Codex\Logs\<date>/*.log`
   — check `install-primary-runtime` lines (expect `problemCount=0`) and
   `desktop_fetch_auth_401` warnings (harmless when using a third-party
   provider instead of ChatGPT auth).
5. `codex doctor` validates the CLI side; a clean doctor + broken Desktop
   usually points to the Desktop renderer/bridge, not the provider config.

### Codex Desktop update check fails with "提交 unknown" / can't reach update server

Separate failure from "won't open": the Desktop's self-update check errors
(`fetch-failed`, UI shows "无法连接更新服务器" / "提交 unknown") even when the
CLI `codex doctor` is healthy.

**Root cause (common on Windows): Electron cannot find git.**

`apps/desktop/electron/main.ts` → `resolveGitBinary()` searches ONLY:
1. `%LOCALAPPDATA%\hermes\git\cmd\git.exe` / `bin\git.exe` (Hermes PortableGit)
2. `C:\Program Files\Git\cmd\git.exe` and `(x86)` variant
3. `%LOCALAPPDATA%\Programs\Git\cmd\git.exe`
4. `findOnPath('git')` — but GUI-launched processes get a MINIMAL PATH

If git is installed on **another drive** (e.g. `D:\Program Files\Git`) and is
not in the Windows **user** PATH, the Desktop finds no git → fetch fails →
"提交 unknown" (current commit unknown). `which git` working in bash is NOT
proof — bash uses `/mingw64/bin/git` from the MSYS distribution.

**Fix — add Git to the Windows user PATH (does not overwrite existing):**
```bash
powershell.exe -Command "
\$currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
\$gitPath = 'D:\Program Files\Git\cmd'
if (\$currentPath -like '*D:\Program Files\Git*') { Write-Host 'already present' }
else { [Environment]::SetEnvironmentVariable('Path', \$currentPath.TrimEnd(';') + ';' + \$gitPath, 'User'); Write-Host 'added' }
"
```

**Verify Electron's search will find it** (simulate `findOnPath` over the user
PATH), then **fully restart the Desktop app** — PATH changes don't apply to
already-running processes.

Also check the CLI-side git connectivity while you're in there (China network):
```bash
git config --global http.https://github.com.proxy http://127.0.0.1:12450
# stale .git/shallow.lock from an interrupted update also blocks fetch:
rm -f /c/Users/Windows/AppData/Local/hermes/hermes-agent/.git/shallow.lock
```

**Same root cause affects Hermes Studio** (Hermes Desktop's own update check, UI shows "分支 main / 提交 unknown" + red "无法连接更新服务器"): Hermes Studio is a separate Electron app (`D:\Program Files\Hermes Studio`) whose `resolveGitBinary()` search mirrors the Codex one (PortableGit → C:\Program Files\Git → PATH). Same fix: append `D:\Program Files\Git\cmd` to the Windows user PATH, fully restart the app, re-check in 设置 → 关于 → 立即检查. The CLI `hermes update --check` may pass while the Desktop still fails — they resolve git differently.

## Examples

See `references/aslnet-example.md` for a complete working example using
ASLNet (`https://api.aslnet.cloud`) with Codex CLI, including model list,
config fragment, env var setup, and curl verification commands.
