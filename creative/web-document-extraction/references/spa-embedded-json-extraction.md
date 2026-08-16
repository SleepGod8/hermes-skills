# SPA / Embedded-JSON extraction (ModelScope MCP 广场, verified 2026-08)

General pattern for sites whose content is NOT in the initial HTML: check for
`window.__xxx_data__` embedded JSON first (curl-able), then fall back to a real
browser (browser_exec) for SPA list pages backed by encrypted APIs.

## Case A: detail pages with embedded JSON — curl is enough

ModelScope MCP detail pages (`https://www.modelscope.cn/mcp/servers/<scope>/<name>`)
embed the full record as a JSON-**string** in `window.__detail_data__` (double-encoded).
No browser needed:

```bash
curl -sL "https://www.modelscope.cn/mcp/servers/@modelcontextprotocol/fetch" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -o ms_page.html
```

```python
import re, json
html = open('ms_page.html', encoding='utf-8', errors='replace').read()
m = re.search(r'window\.__detail_data__\s*=\s*"(.*?)";', html, re.S)
data = json.loads(m.group(1).encode().decode('unicode_escape'))
```

Useful fields: `Name`, `ChineseName`, `AbstractCN`, `CallVolume`, `ViewCount`, `Stars`,
`License`, `Verifed`, `Publisher`, `GmtCreated`/`GmtUpdated` (unix seconds),
`SupportedDeployTransportType` (`["streamable_http","sse"]`), `ServerConfig` (the official
mcpServers JSON — exact install command/token env for that server), `Tools` (array of
{name, description, inputSchema}), `ReadmeCN`/`Readme`.

## Case B: SPA list page — browser required

- `https://www.modelscope.cn/mcp/servers` (MCP 广场) renders an empty shell:
  `window.__detail_data__ = ""`; the real list comes from an **encrypted frontend API**
  (minified `umi.js` contains the marker string `"aes-mcp"`). All guessed REST endpoints
  return the SPA fallback HTML (HTTP 200 + ~2.9KB index), so curl cannot list servers.
- **Navigation trap**: going straight to `/mcp/servers` can 404-redirect to a bogus route
  (`/models/mcp/servers`, "模型详情页"). Navigate to `https://www.modelscope.cn/mcp`
  directly, or click the "MCP 广场" nav link.
- Use `browser_exec`. First use on the Hermes desktop requires the user to authorize
  remote debugging: Chrome opens `chrome://inspect/#remote-debugging` → tick **"Allow
  remote debugging for this browser instance"** → **Allow**; Chrome shows ONE more Allow
  popup on the next connect attempt (expected, not a re-ask). Retry after the user confirms.
- Extract cards text-first (no screenshots): `js("document.body.innerText")`, split lines —
  each card is `Name / Hosted|Local / category / license / description / @publisher /
  calls / views / stars`. Category counts parse with regex `分类名\n(\d+)` (浏览器自动化 596,
  搜索工具 1405, 开发者工具 3368, etc.). Pager is numbered (1..5); collect server links with
  `Array.from(document.querySelectorAll('a')).filter(a => a.href.includes('/mcp/servers/'))`.

## Tool selection rule (verified 2026-08)

| Task | Tool |
|------|------|
| JSON / API endpoints | `curl` (lightest) |
| Static HTML → Markdown | Fetch MCP (`mcp__fetch__fetch`) — ms-fast, no browser |
| SPA (React/Vue), login walls, interaction | `browser_exec` — heavy but renders JS |

Fetch MCP is NOT redundant once browser_exec exists: it is the fast path for static pages;
browser_exec is the fallback for dynamic/JS-rendered content. On this machine both are
configured and both work.
