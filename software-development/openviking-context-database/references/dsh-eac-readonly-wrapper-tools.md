# DSH EAC OpenViking read-only wrapper tools

Session-derived implementation notes for DeepSeek Harness EAC when the official OpenViking MCP tools do not appear in the model's tool list.

## Symptom

- The DSH EAC session shows `上下文注入 · openviking-memory` and the model sees `<openviking-context>` blocks, so OpenViking recall is working.
- The same session does **not** expose `mcp__openviking__grep`, `mcp__openviking__read`, or `mcp__openviking__find`.
- Tool enumeration may show only the active preset's fixed tools, e.g. `functions.bash`, `functions.str_replace_editor`, `functions.skill_search`, `functions.skill_load`, `functions.dev_tool_search`, `multi_tool_use.parallel`.

Interpretation: OpenViking memory recall/capture and MCP proxy startup are separate from the current agent's model-facing tool surface.

## Working workaround

Create a small DSH plugin that registers ordinary DSH tools which call OpenViking `/mcp` directly and expose only safe read operations:

- `openviking_find` → MCP `find`
- `openviking_grep` → MCP `grep`
- `openviking_read` → MCP `read`

Keep it read-only: do not expose `remember`, `write`, `edit`, `forget`, or `add_resource` unless the user explicitly requests a write-capable integration.

## Key implementation detail

Register tools both globally and per agent. In EAC, some agent presets filter inherited/global tools; global `ctx.tools.register(...)` can log as registered while the model still cannot see it. Add an `agent/session-start` hook and register the same definitions into `agent.ctx.tools`:

```js
import { defineTool } from '@deepseek-ai/dsh-tools'

export const name = 'openviking-readonly-tools'
export const inject = ['tools', 'agents']

export function apply(ctx, input = {}) {
  const config = normalizeConfig(input)
  const definitions = makeDefinitions(config)

  // Useful for registry/global probes.
  for (const definition of definitions) ctx.tools.register(definition)

  // Required for presets that filter inherited global tools.
  ctx.on('agent/session-start', ({ agent }) => {
    for (const definition of definitions) agent.ctx.tools.register(definition)
  })

  console.log('[openviking-readonly-tools] registered openviking_find/openviking_grep/openviking_read globally and per agent')
}
```

## EAC profile details observed

- Real EAC desktop profile: `web-desktop`, not `web`.
- Installed package path: `C:/Users/<user>/.dsh/profiles/web-desktop/node_modules/dsh-openviking-readonly-tools`.
- Local source/tarball can live under `C:/Users/<user>/.dsh/local-plugins/` and `C:/Users/<user>/.dsh/*.tgz` to avoid Windows paths with spaces.
- Patch shape:

```yaml
- id: openviking-readonly-tools
  config:
    endpoint: http://127.0.0.1:1933
    apiKey: "<redacted>"
    account: local
    user: master
    peerId: dsh-eac-readonly-tools
    timeoutMs: 15000
    maxOutputChars: 12000
```

## Verification

1. DSH web log should contain:

```text
[openviking-readonly-tools] registered openviking_find/openviking_grep/openviking_read globally and per agent
```

2. In a new EAC session ask for available tools and then call:

```text
请用 openviking_grep 查询 OVREMEMBER_b403810474，搜索范围 uri=viking://user，node_limit=2。不要用 bash。
```

3. If it still says unavailable, verify the session is new and that the active preset is not enforcing a hard static allowlist at request assembly time.

## Pitfalls

- Do not conclude that OpenViking is broken merely because `mcp__openviking__*` is unavailable. Recall may be working while active MCP tools are hidden.
- Do not stop at a log saying `ctx.tools.register` succeeded. Confirm model-facing visibility in a new session.
- Reinstalling a same-version local tarball may leave pnpm saying `Already up to date`; if necessary, copy the edited `index.js` into the installed `node_modules` package or bump the package version before reinstalling.
- Keep API keys redacted in logs and reports.
