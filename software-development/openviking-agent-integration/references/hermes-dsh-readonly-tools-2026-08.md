# Hermes default + DSH EAC OpenViking read-only tools (2026-08)

This reference captures a validated Windows integration path from a session where OpenViking was already running locally in Docker and the user wanted **read-only model tools** for both DeepSeek Harness EAC and Hermes default.

## Local OpenViking service facts

- Endpoint: `http://127.0.0.1:1933`
- MCP endpoint: `http://127.0.0.1:1933/mcp`
- Container: `openviking`
- Data/config: `E:/Hermes workspace/openviking-data/ov.conf`
- Auth mode: `trusted`
- Account/user used in tests: `local` / `master`
- Do not print full root API key or provider API keys.

## DSH EAC validated shape

Goal: make DSH EAC expose:

- `openviking_find`
- `openviking_grep`
- `openviking_read`

while the official OpenViking DSH plugin handles recall/context injection.

Important details:

- Real EAC profile was `C:/Users/80704/.dsh/profiles/web-desktop`, not `web`.
- Official `@openviking/dsh-memory-plugin@0.2.1` recall worked, but `mcp__openviking__*` tools were not model-visible.
- A separate wrapper plugin using ordinary DSH `ctx.tools.register(defineTool(...))` worked at the backend level.
- Tools were still invisible until the active `anchored-standard` preset was patched, because `tool-bootstrap.mjs` filters `assembled.tools` in `system-prompt/assemble`.

Patch pattern for `anchored-standard/tool-bootstrap.mjs`:

```js
const RESIDENT_LOCAL_TOOLS = ['openviking_find', 'openviking_grep', 'openviking_read']
```

Include `RESIDENT_LOCAL_TOOLS` in both the promoted keep-set and, if immediate visibility is desired, the controlled/bootstrap keep-set.

Validation prompt in a new DSH EAC session:

```text
列出当前所有工具名称，检查是否有 openviking_find、openviking_grep、openviking_read。
```

Then:

```text
请用 openviking_grep 查询 OVREMEMBER_b403810474，搜索范围 uri=viking://user，node_limit=2。不要用 bash。
```

Successful observed result: the DSH model called `openviking_grep` directly and found 2 hits under `viking://user/master/sessions/20260821_125954_a8a0eb/history/archive_001/messages.jsonl`.

## Hermes default validated shape

User requirement: add read-only OpenViking tools to Hermes default **without replacing native memory**.

Created plugin:

```text
C:/Users/80704/AppData/Local/hermes/plugins/openviking-readonly-tools/
  plugin.yaml
  __init__.py
```

`plugin.yaml` should declare `provides_tools` for the three tools and optional settings (`endpoint`, `account`, `user`, `peer_id`, `ov_conf_path`, `timeout_ms`, `max_output_chars`).

Hermes plugin code uses `ctx.register_tool(...)` with `toolset="openviking"`. The handler talks to OpenViking MCP over HTTP using only standard library modules (`urllib.request`, `json`) so no extra package install is needed.

Enable:

```bash
hermes plugins enable openviking-readonly-tools
```

Expected CLI surface:

```text
hermes tools list
✓ enabled  openviking  🔌 Openviking
```

Check no memory provider replacement occurred by reading default config; in the validated run `memory.provider` remained `None`.

Backend smoke test:

- Import plugin module directly.
- Fake a minimal `ctx` with `get_config` and `register_tool`.
- Register tools.
- Call `openviking_grep` handler with:
  ```json
  {"pattern":"OVREMEMBER_b403810474","uri":"viking://user","node_limit":2}
  ```
- Observed success: JSON result had `ok: true`, `rawTool: grep`, and 2 marker hits.

## Tool behavior contract

- `openviking_find`: semantic search; accepts `query`, optional `target_uri`, `limit`, `min_score`.
- `openviking_grep`: exact/regex search; accepts `uri`, `pattern` string or string array, optional `case_insensitive`, `node_limit`.
- `openviking_read`: read one or more `viking://` URIs; reject local filesystem paths.

All outputs should be bounded, e.g. 12000 chars, and all HTTP calls should time out.

## Mistakes to avoid

- Do not install OpenViking into Hermes' Python environment; keep it as a local service.
- Do not switch Hermes default memory provider during a read-only tool request.
- Do not expose OpenViking write/delete tools by default.
- Do not assume DSH model visibility from plugin logs alone; final preset catalog filtering can remove tools.
- Do not use DSH test profile `web` when EAC Desktop is actually using `web-desktop`.
