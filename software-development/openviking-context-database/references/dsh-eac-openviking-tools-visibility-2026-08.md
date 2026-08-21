# DSH EAC OpenViking integration: context injection vs MCP tools

Session-derived finding for the user's DeepSeek Harness EAC setup.

## Environment observed

- EAC app: `E:/Deepseek Harness EAC`
- Real desktop DSH profile: `web-desktop`
- Test profile that can be misleading: `web`
- OpenViking service: `http://127.0.0.1:1933`
- Plugin: `@openviking/dsh-memory-plugin@0.2.1`

## Key lesson

Installing and validating `@openviking/dsh-memory-plugin` in `web` is not enough for EAC desktop sessions. The actual EAC desktop process used `--profile web-desktop`, so the plugin must be installed and configured there.

After installation into `web-desktop`, DSH EAC showed `上下文注入 · openviking-memory`, and the model saw `<openviking-context>...</openviking-context>`. This proves OpenViking recall/context injection is working.

However, the same session did **not** expose model-callable MCP tools. The model listed only:

- `functions.bash`
- `functions.str_replace_editor`
- `functions.skill_search`
- `functions.skill_load`
- `functions.dev_tool_search`
- `multi_tool_use.parallel`

It did not have:

- `mcp__openviking__grep`
- `mcp__openviking__read`
- `mcp__openviking__find`

## Interpretation

Treat OpenViking DSH EAC integration as two independent verification layers:

1. **Recall/context injection** — success when the UI shows `上下文注入 · openviking-memory` or the model can see `<openviking-context>` blocks.
2. **MCP tool exposure** — success only when the current agent's actual available tool list includes `mcp__openviking__*` names.

A running `mcp-proxy.mjs` process and a successful standalone JSON-RPC `tools/list` test prove backend connectivity, but do **not** guarantee the current DSH agent/preset exposes those tools to the model.

## Practical guidance

- Always check the live EAC process command line before installing: look for `--profile web-desktop` vs `--profile web`.
- Verify tool visibility from inside a new DSH session by asking the model to list actual available tools.
- If OpenViking context injection works but MCP tools remain absent, do not keep reinstalling the same plugin. The likely issue is the current agent preset/tool catalog filtering or DSH EAC's model-facing tool surface.
- For active read/search operations in this setup, prefer a small EAC wrapper plugin that exposes safe ordinary tools such as `openviking_find`, `openviking_grep`, and `openviking_read`, instead of relying on `mcp__openviking__*` visibility.
