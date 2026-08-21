---
name: openviking-context-database
description: "Use when integrating OpenViking memory with agent tools."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [openviking, memory, context-database, mcp, agent-integration, dsh, hermes]
---

# OpenViking Context Database

Use when the user asks whether OpenViking is useful, wants to deploy it, connect it to Hermes/DSH/other coding agents, import agent logs, or use it as a shared long-term context database.

## Core framing

OpenViking is an agent-native context database, not just a vector DB. It stores memories, resources, and skills under a virtual `viking://` filesystem and exposes deterministic browsing/search primitives (`ls`, `tree`, `find`, `grep`, `read`) plus MCP/REST/CLI integrations.

Good positioning for this user:

- Keep Hermes native memory for short, high-priority facts that must be injected every session.
- Use OpenViking as a second, larger, searchable context store for project docs, long persona/worldbuilding references, session history, resources, and cross-agent memory.
- Treat it as an external service; do **not** install/upgrade it inside the Hermes Python environment unless dependencies are solved together and verified.

## Evaluation workflow

1. Inspect upstream docs/repo before answering: README, `docs/*/agent-integrations/*`, deployment/config guides, and relevant `examples/*memory-plugin*` packages.
2. Identify integration mode for the target agent:
   - Hermes: built-in MemoryProvider; configure with `hermes memory setup openviking` and verify with `hermes memory status`.
   - DSH: `@openviking/dsh-memory-plugin` Cordis plugin; verify `dsh --profile web --dump-config` includes `openviking-memory` and a session exposes `mcp__openviking__*` tools.
   - Generic MCP clients: connect to `/mcp` with API key/OAuth depending on client.
3. Recommend staged rollout:
   - Run OpenViking service first and verify `/health`.
   - Test CLI queries (`ov status`, `ov add-resource`, `ov find`, `ov tree`, `ov grep`).
   - Import a few non-critical resources before switching any agent memory provider.
   - Test on a non-primary Hermes profile before changing the default profile.
   - Only then attempt DSH/EAC integration.
4. Call out AGPLv3 and operational weight when relevant.

## Local deployment quick checks

Standalone:

```bash
openviking-server init
openviking-server doctor
openviking-server
curl http://localhost:1933/health
```

Docker:

```bash
docker run -d \
  --name openviking \
  -p 1933:1933 \
  -v ~/.openviking:/app/.openviking \
  --restart unless-stopped \
  ghcr.io/volcengine/openviking:latest
curl http://localhost:1933/health
```

CLI smoke test:

```bash
ov status
ov add-resource https://github.com/volcengine/OpenViking --wait
ov tree viking://resources/ -L 2
ov find "what is openviking"
```

## Hermes integration notes

- OpenViking docs state Hermes has built-in OpenViking memory provider support; no separate Hermes plugin is required.
- Configure through `hermes memory setup openviking`; verify through `hermes memory status`.
- Prefer a test profile first. For this user, avoid immediately replacing the `default` profile memory because the current Hermes memory contains persona-critical facts.
- Use OpenViking for bulky searchable data; keep concise must-know facts in Hermes native memory.

## DSH / DSH EAC integration notes

- Official DSH integration is `examples/dsh-memory-plugin` / `@openviking/dsh-memory-plugin`.
- Official install path assumes standard `dsh` profile/plugin management:

```bash
bash <(curl -fsSL https://ovrelease.tos-cn-beijing.volces.com/memory-plugin-shared/install.sh)
# or
 dsh plugin --profile web add @openviking/dsh-memory-plugin
```

- Verify with `dsh --profile web --dump-config`; runtime should inject OpenViking context and expose `mcp__openviking__*` tools.
- For this user's DeepSeek Harness EAC desktop build, do not assume the official CLI plugin install works. EAC often requires built-in plugin synchronization via `resources/app/assets/plugins`, `COMPANION_PLUGINS`, profile node_modules, and `cordis.patch.yml`. Validate compatibility before promising success.

## Pitfalls

- Do not conflate OpenViking with Milvus/Dify-style black-box RAG; emphasize the `viking://` filesystem and traceable retrieval.
- Do not advise installing OpenViking into Hermes' own Python venv. The upstream Hermes integration doc recommends isolating OpenViking and connecting over HTTP.
- When multiple agents/profiles use one OpenViking service, configure account/user/actor-peer or peer scope to avoid cross-project memory bleed.
- DSH EAC compatibility is a separate validation problem from standard CLI DSH support.

## References

- See `references/openviking-hermes-dsh-evaluation.md` for the session-derived Hermes/DSH evaluation checklist and concrete facts observed from the upstream repo.
