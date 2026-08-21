# OpenViking Hermes/DSH evaluation notes

Session-derived facts from inspecting `volcengine/OpenViking` in August 2026. Use as a quick checklist; re-check upstream docs before making current claims.

## Upstream positioning

- README calls OpenViking an open-source context database for AI agents.
- Data lives under `viking://` with resources, user memories, user resources, skills, and peers.
- Content is processed into L0 abstract, L1 overview, and L2 details.
- Retrieval is intended to be observable and directory-recursive, not a black-box vector store only.
- Open-source license in repo metadata is AGPL-3.0.

## Repo structure observed

Important directories:

- `openviking/`: Python server/core/storage implementation.
- `openviking/server/`: FastAPI server, MCP endpoint, auth, routers.
- `openviking/storage/`: virtual filesystem, vector DB adapters, local vector index.
- `examples/dsh-memory-plugin/`: official DSH Cordis memory plugin.
- `examples/memory-plugin-shared/`: shared JS plugin runtime and installer.
- `docs/zh/agent-integrations/`: integration docs for Hermes, DSH, MCP, capability matrix.
- `web-studio/`: frontend UI.
- `crates/`: Rust CLI/RAGFS components.
- `src/`: C++ vector-index engine.

Approximate local code shape from a checkout: Python dominates, with Rust, TypeScript/TSX, MJS, C++, Markdown docs.

## Hermes integration facts

OpenViking docs state:

- Hermes Agent has a bundled OpenViking MemoryProvider.
- No separate Hermes plugin is required.
- Configure with:

```bash
hermes memory setup openviking
hermes memory status
```

Operational interpretation for this user:

- Do not replace the default Hermes memory immediately.
- Test in a non-primary profile first.
- Keep Hermes native memory for compact must-load facts.
- Put bulky searchable context in OpenViking.

Capability matrix noted for Hermes:

- Native registration of 6 `viking_*` tools.
- Can search memory/resource/skill.
- Can write memory via `viking_remember`.
- Can write resources through multi-protocol ingest.
- No skill write through Hermes integration.
- Automatic recall exists, but session-id wiring is partial in some fallback paths.
- Offline compensation is in-process queue, not durable disk queue.

## DSH integration facts

Official DSH docs point to `examples/dsh-memory-plugin` and package `@openviking/dsh-memory-plugin`.

Official installation:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/volcengine/OpenViking/main/examples/memory-plugin-shared/install.sh)
# China mirror:
bash <(curl -fsSL https://ovrelease.tos-cn-beijing.volces.com/memory-plugin-shared/install.sh)
# Manual:
dsh plugin --profile web add @openviking/dsh-memory-plugin
```

Verification:

```bash
dsh --profile web --dump-config
```

Expected runtime signs:

- `openviking-memory` appears in profile config.
- Session starts with OpenViking context injection.
- Model sees `mcp__openviking__*` tools.
- `OV_DEBUG_LOG` can be set for troubleshooting.

Behavior:

- Cordis in-process plugin, not just an external hook.
- Session start injects profile and memory index.
- Each model step does semantic recall and appends persistent context.
- Captures user/assistant messages and optional tool results.
- Commits after token threshold; failed writes go to a pending queue.
- Session id maps to `dsh-<session-id>`.

DSH EAC caution:

- The official plugin targets standard `dsh` plugin/profile flow and peer deps around `@deepseek-ai/dsh-*` rc packages.
- The user's DeepSeek Harness EAC desktop build may require the separate built-in plugin synchronization path already known for EAC: plugin assets under `resources/app/assets/plugins`, `COMPANION_PLUGINS` registration, profile node_modules sync, and Cordis patch validation.
- Treat EAC compatibility as a validation task, not guaranteed by upstream DSH docs.

## MCP facts

- OpenViking exposes `/mcp` directly.
- Standard MCP clients can use `mcpServers.openviking.url = https://.../mcp` plus Authorization header when API key auth is enabled.
- Local dev without `root_api_key` can be unauthenticated.
- MCP tool surface includes retrieval, memory, resource, watch, and filesystem operations.

## Suggested staged rollout

1. Start OpenViking standalone or Docker and verify `/health`.
2. Configure CLI and smoke-test `ov status`.
3. Add one resource and query it with `ov find`, `ov tree`, and `ov grep`.
4. Try Hermes integration in a test profile.
5. Only after stability, consider default Hermes provider changes.
6. Try standard DSH plugin install if CLI DSH exists.
7. For DSH EAC, inspect actual EAC plugin loading path before installing.
