---
name: openviking-agent-integration
description: "Use when connecting OpenViking to Hermes/DSH agents."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [openviking, memory, mcp, hermes, dsh, readonly-tools, windows]
---

# OpenViking Agent Integration

Use when the user asks to connect OpenViking to Hermes Agent, DSH / DeepSeek Harness EAC, or another local agent as a shared searchable context/memory layer.

Default posture for this user: **prefer read-only tools first**. Do not replace Hermes default memory provider unless the user explicitly asks. Do not expose write/delete OpenViking tools to model sessions by default.

## Architecture pattern

OpenViking should run as an isolated local service, typically Docker-backed, and agents should connect over HTTP/MCP:

- OpenViking endpoint: usually `http://127.0.0.1:1933`.
- Data/config: e.g. `E:/Hermes workspace/openviking-data/ov.conf`.
- Use account/user/peer headers to avoid context bleed when multiple agents share one service.
- Keep concise durable facts in Hermes memory; put bulky searchable session/project context in OpenViking.

## Hermes default: add read-only tools without replacing memory

Use this when the user wants Hermes to query OpenViking but keep the native Hermes memory provider.

1. Create a profile-local/user plugin under default Hermes home:
   ```text
   C:/Users/80704/AppData/Local/hermes/plugins/openviking-readonly-tools/
   ```
2. Add `plugin.yaml` declaring `provides_tools`:
   ```yaml
   name: openviking-readonly-tools
   version: "0.1.0"
   description: "Read-only OpenViking tools for Hermes: openviking_find, openviking_grep, openviking_read."
   provides_tools:
     - openviking_find
     - openviking_grep
     - openviking_read
   config_schema:
     endpoint:
       type: string
       default: "http://127.0.0.1:1933"
     account:
       type: string
       default: "local"
     user:
       type: string
       default: "master"
     peer_id:
       type: string
       default: "hermes-default-readonly-tools"
     ov_conf_path:
       type: string
       default: "E:/Hermes workspace/openviking-data/ov.conf"
   ```
3. In `__init__.py`, use `ctx.register_tool(...)` to register only:
   - `openviking_find` → OpenViking MCP `find`
   - `openviking_grep` → OpenViking MCP `grep`
   - `openviking_read` → OpenViking MCP `read`
4. Do **not** call `hermes memory setup openviking` for default unless the user explicitly requests memory-provider replacement.
5. Enable and verify:
   ```bash
   hermes plugins enable openviking-readonly-tools
   hermes tools list | grep -i openviking
   ```
6. Changes take effect on the next Hermes session or `/reset`.
7. Direct smoke test should call a known marker through the handler or a fresh Hermes session:
   ```text
   openviking_grep pattern=OVREMEMBER_b403810474 uri=viking://user node_limit=2
   ```

## DSH / DeepSeek Harness EAC: official recall + read-only wrapper

Use the official `@openviking/dsh-memory-plugin` for automatic recall/context injection. If model-facing MCP tools do not appear in EAC sessions, add a minimal wrapper plugin that exposes ordinary DSH tools:

- `openviking_find`
- `openviking_grep`
- `openviking_read`

Rules:

- Install into the real EAC profile, commonly `C:/Users/80704/.dsh/profiles/web-desktop`, not only a test `web` profile.
- Keep wrapper output bounded and request timeout bounded.
- Do not expose `remember`, `write`, `edit`, `forget`, or `add_resource`.
- Do not pass `viking://` URIs to bash/filesystem tools.

If tools are registered in logs but invisible to the model, inspect the active agent preset. `anchored-standard` can filter the final `assembled.tools` catalog in `system-prompt/assemble`; add only the three read-only OpenViking tools to its keep-set if the user wants them resident.

## Verification checklist

- Service reachable: OpenViking container or server is running on the configured endpoint.
- Tool registration visible: `hermes tools list` or DSH tool list shows the three read-only tools.
- Backend works: known marker grep returns real `viking://...` hits.
- No provider replacement: Hermes `memory.provider` remains unchanged when the request is read-only tools only.
- Secrets safe: never print full OpenViking root API key or upstream provider keys.

## Pitfalls

- Official DSH recall working does **not** imply model-facing MCP tools are visible.
- DSH host `registered` logs only prove registry insertion, not final prompt catalog exposure.
- EAC Desktop often runs `web-desktop`; patching `web` alone is a common false fix.
- For Hermes, plugin tool changes require a new session/reset before the live model sees the new tools.
- Use `ctx.register_tool` for Hermes plugins; direct edits to Hermes core `tools/` work but are less maintainable.
- If OpenViking is in `trusted` auth mode, still avoid echoing `root_api_key`; read it locally in code if needed.

## References

- `references/hermes-dsh-readonly-tools-2026-08.md` — session-derived implementation details for Hermes default + DSH EAC read-only OpenViking tools.
