# DSH EAC OpenViking read-only wrapper validation (2026-08)

## When to use

Use this when the official `@openviking/dsh-memory-plugin` loads and injects `<openviking-context>`, but the current DSH EAC agent session still does not expose `mcp__openviking__grep/read/find` in its model-visible tool catalog.

Observed symptom in DSH EAC:

- UI shows `上下文注入 · openviking-memory`.
- Model can see `<openviking-context>` blocks.
- Asking for available tools lists only standard tools such as `functions.bash`, `functions.str_replace_editor`, `functions.skill_search`, `functions.skill_load`, `functions.dev_tool_search`, `multi_tool_use.parallel`.
- `mcp__openviking__grep`, `mcp__openviking__read`, `mcp__openviking__find` are absent.

Interpretation: OpenViking recall/capture is working, but the MCP bridge tools are not exposed to the selected DSH agent preset/tool catalog.

## Working fallback pattern

Create a normal DSH plugin that registers three read-only tools directly via `@deepseek-ai/dsh-tools`:

- `openviking_find`
- `openviking_grep`
- `openviking_read`

These wrap OpenViking's `/mcp` streamable HTTP endpoint and call raw MCP tools `find`, `grep`, and `read`. Do not expose write/delete tools (`remember`, `write`, `edit`, `forget`, `add_resource`) in the first rollout.

## Minimal package shape

`package.json`:

```json
{
  "name": "dsh-openviking-readonly-tools",
  "version": "0.1.0",
  "type": "module",
  "main": "index.js",
  "exports": { ".": "./index.js", "./package.json": "./package.json" },
  "files": ["index.js", "cordis.patch.yml", "package.json"],
  "dsh": { "bundle": { "patch": "./cordis.patch.yml" } },
  "peerDependencies": { "@deepseek-ai/dsh-tools": "*" },
  "engines": { "node": ">=20" }
}
```

`cordis.patch.yml`:

```yaml
- insert:
    - id: openviking-readonly-tools
      name: dsh-openviking-readonly-tools
```

`index.js` registers tools with:

```js
import { defineTool } from '@deepseek-ai/dsh-tools'
export const name = 'openviking-readonly-tools'
export const inject = ['tools']

export function apply(ctx, config) {
  ctx.tools.register(defineTool({ name: 'openviking_grep', /* ... */ }))
  ctx.tools.register(defineTool({ name: 'openviking_find', /* ... */ }))
  ctx.tools.register(defineTool({ name: 'openviking_read', /* ... */ }))
}
```

The tool implementation should:

1. `POST /mcp` `initialize` without `Mcp-Session-Id`.
2. Capture `mcp-session-id` response header.
3. Send `notifications/initialized` with that session id.
4. Send `tools/call` with the target raw OpenViking tool name.
5. Parse either JSON or `text/event-stream` responses.
6. Return text from `result.content[].text`, truncated to a safe max output length.

Headers:

```text
Content-Type: application/json
Accept: application/json, text/event-stream
MCP-Protocol-Version: 2025-06-18
Authorization: Bearer <api key>        # if configured
X-OpenViking-Account: <account>        # if configured
X-OpenViking-User: <user>              # if configured
X-OpenViking-Actor-Peer: <peerId>      # if configured
```

## EAC install path used

For EAC desktop the real profile was `web-desktop`, not `web`:

```bash
APP='E:/Deepseek Harness EAC/resources/app'
npm pack --silent
cp dsh-openviking-readonly-tools-0.1.0.tgz C:/Users/80704/.dsh/dsh-openviking-readonly-tools-0.1.0.tgz
node "$APP/node_modules/@deepseek-ai/dsh/lib/bin.js" plugin --profile web-desktop add 'C:/Users/80704/.dsh/dsh-openviking-readonly-tools-0.1.0.tgz'
```

Add runtime config to `C:/Users/80704/.dsh/profiles/web-desktop/cordis.patch.yml`:

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

Back up `package.json`, `pnpm-lock.yaml`, and `cordis.patch.yml` before installing.

## Verification

After restarting EAC, `dsh-web.log` should contain:

```text
[openviking-readonly-tools] registered openviking_find/openviking_grep/openviking_read
```

Independent Node-level verification can import the installed package from the profile `node_modules` so peer dependency resolution works:

```js
const mod = await import(pathToFileURL('C:/Users/80704/.dsh/profiles/web-desktop/node_modules/dsh-openviking-readonly-tools/index.js').href)
const regs = []
const ctx = { tools: { register: (tool) => { regs.push(tool); return () => {} } } }
mod.apply(ctx, { endpoint, apiKey, account: 'local', user: 'master', peerId: 'dsh-eac-readonly-test' })
console.log(regs.map(t => t.name))
await regs.find(t => t.name === 'openviking_grep').execute({ pattern: 'OVREMEMBER_b403810474', uri: 'viking://user', node_limit: 2 }, {})
```

Expected registered tool names:

```text
openviking_find, openviking_grep, openviking_read
```

In DSH EAC, test with:

```text
请用 openviking_grep 查询 OVREMEMBER_b403810474，搜索范围 uri=viking://user，node_limit=2。不要用 bash。
```

## Safety notes

- Keep this wrapper read-only unless the user explicitly asks for write/delete support.
- Use names `openviking_*`, not `mcp__openviking__*`, to avoid confusion with DSH's official MCP bridge naming.
- Do not conclude official MCP support is broken globally; this is a fallback for EAC/preset cases where recall is injected but MCP tools are not model-visible.
