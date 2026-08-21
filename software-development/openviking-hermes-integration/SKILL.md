---
name: openviking-hermes-integration
description: Use when integrating OpenViking with Hermes or DSH.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes-agent, openviking, mcp, plugins, memory, dsh]
    related_skills: [hermes-agent, hermes-mcp-configuration, hermes-agent-skill-authoring]
---

# OpenViking × Hermes / DSH Integration

## Overview

Use this skill when wiring OpenViking into Hermes Agent or DSH/EAC workflows. The preferred pattern is **OpenViking as a shared searchable archive**, not as a wholesale replacement for Hermes native memory unless the user explicitly asks for that migration.

The safe baseline is:

```text
Hermes native memory = keep
OpenViking = MCP-backed shared retrieval/archive layer
Read tools = find / grep / read
Write tool = controlled archive only, not raw write/edit/forget
```

This skill captures the validated pattern from integrating a local OpenViking MCP server with Hermes plugins and DSH recall.

## When to Use

- User asks whether OpenViking is useful for Hermes, DSH, multi-agent development, or novel workshops.
- User asks to add OpenViking tools to Hermes Agent.
- User wants shared memory/context across Hermes profiles, DSH/EAC, coding agents, or creative workshops.
- User wants a safe write path into OpenViking without exposing unrestricted `write`, `edit`, or `forget`.
- User asks to archive project decisions, agent handoffs, validation evidence, novel canon, plot facts, or logic-review results.

Do **not** use this skill for generic MCP setup unless OpenViking is involved; use `hermes-mcp-configuration` for ordinary MCP server configuration.

## Recommended Architecture

### Stable roles

```text
Hermes default
  - Orchestrates, summarizes, reviews, and decides what is worth archiving.
  - Uses OpenViking tools for retrieval and controlled archival.

DSH / EAC
  - Handles local coding/debugging contexts.
  - Uses OpenViking recall/context injection and explicit search/read tools where available.

OpenViking
  - Shared searchable archive and context database.
  - Stores durable project/novel artifacts, not raw every-turn chatter.
```

### Do not replace native memory by default

Before and after adding OpenViking tools, verify Hermes config still does not silently switch the native memory provider unless the user requested it. The intended safe state is:

```text
memory.provider = None or existing native provider
OpenViking tools = additional capabilities
```

## Hermes Plugin Pattern

For a local user plugin, place files under the active profile's plugin directory, for example on Windows default profile:

```text
C:/Users/<user>/AppData/Local/hermes/plugins/<plugin-name>/
  plugin.yaml
  __init__.py
```

A practical toolset is:

```text
openviking_find     semantic retrieval, read-only
openviking_grep     exact/regex search, read-only
openviking_read     read viking:// URI content, read-only
openviking_archive  controlled structured archive write
```

Register all tools under a single toolset such as `openviking` so `hermes tools list` shows a compact capability group.

## MCP HTTP Calling Pattern

OpenViking's MCP endpoint can be used over HTTP JSON-RPC at:

```text
http://127.0.0.1:1933/mcp
```

Validated headers include:

```text
Content-Type: application/json
Accept: application/json, text/event-stream
MCP-Protocol-Version: 2025-06-18
Authorization: Bearer <root_api_key if configured>
X-OpenViking-Account: local
X-OpenViking-User: master
X-OpenViking-Actor-Peer: hermes-default-tools
```

Robust clients should accept both ordinary JSON and SSE (`text/event-stream`) responses. For SSE, parse `data:` blocks and ignore comments/empty events.

Minimal call sequence:

1. `initialize`
2. `notifications/initialized`
3. `tools/call` for `find`, `grep`, `read`, or the underlying `write` used by a controlled wrapper.

Completion criterion: a test call can list or call OpenViking tools and parse the returned JSON-RPC result without assuming a session header is present.

## Controlled Archive Tool

Expose a safe `openviking_archive` wrapper instead of raw `write`. It should write structured Markdown to an archive namespace and reject unsafe inputs.

### Required inputs

```json
{
  "workspace": "smart-wealth",
  "category": "decision",
  "title": "ADR-003 风控模块不使用 RAG 做最终判断",
  "status": "approved",
  "summary": "短摘要",
  "content": "Markdown 正文",
  "source": "Hermes default / Athena / DSH EAC",
  "tags": ["smart-wealth", "risk", "adr"]
}
```

### Recommended categories

```text
decision
constitution
handoff
validation
troubleshooting
canon
character
worldbuilding
plot
style
review
reference
```

### Recommended statuses

```text
draft
proposed
approved
canon
superseded
rejected
archived
```

### URI policy

Generate URIs, do not let the model freely choose arbitrary destinations:

```text
viking://user/master/archives/<workspace>/<category>/<YYYYMMDD>-<title-slug>-<hash>.md
```

Use `mode=create` so accidental overwrites fail. If updates are needed later, create a superseding archive record or require an explicit edit workflow with user confirmation.

### Markdown shape

Each archive should include YAML frontmatter:

```md
---
workspace: "smart-wealth"
category: "decision"
status: "approved"
title: "ADR-003 风控模块不使用 RAG 做最终判断"
source: "Hermes default"
created_at: "2026-08-21T07:51:47+00:00"
tags: ["smart-wealth", "risk", "adr"]
schema: openviking_archive.v1
---

# ADR-003 风控模块不使用 RAG 做最终判断

## Summary

...

## Content

...
```

### Safety gates

A controlled archive wrapper should:

- Require `workspace`, `category`, `title`, and `content`.
- Enforce category/status allowlists.
- Limit title/content size.
- Normalize `workspace`, `category`, `status`, and tags into safe slugs.
- Reject likely secrets: API keys, bearer tokens, passwords, GitHub PATs, `sk-...` tokens.
- Call OpenViking raw `write` internally with `mode=create`, preferably `wait=true` where supported.
- Return the generated `viking://` URI and indexing status.

## Multi-Agent Development Usage

For multi-agent development, OpenViking should supplement `.agents/`, `AGENTS.md`, and project constitution files.

Recommended authority stack:

```text
PROJECT_CONSTITUTION.md / AGENTS.md = project law
.agents/task-board.yaml = current execution state
OpenViking archives = searchable history, decisions, handoffs, validation evidence
Hermes memory = compact long-term user/environment facts
Skills = reusable process
```

Archive especially:

- Architecture decisions and ADRs.
- Frozen interfaces, schema decisions, and API contracts.
- Agent handoffs and integration checkpoints.
- Validation evidence: exact commands and real outputs.
- Troubleshooting conclusions that are durable across sessions.

Do not archive raw failed logs or every intermediate thought. Archive the durable conclusion and enough evidence to recover context.

## Novel Workshop Usage

For novel workshops, OpenViking should supplement `.novel/bible.md`, not replace it.

Recommended authority stack:

```text
.novel/bible.md = canon source of truth
.novel/tasks.md / checkpoints = current workshop state
OpenViking archives = searchable canon history, rejected ideas, role reports, reviews
Hermes memory = user creative preferences
Skills = workshop process
```

Archive especially:

- Owner-approved canon decisions.
- Character cards and relationship changes.
- Worldbuilding rules and magic-system constraints.
- Plot outlines, foreshadowing records, and timeline summaries.
- Logic-review findings and rejected ideas.

When OpenViking search finds relevant novel material, treat it as evidence. The W0/editor role should reconcile it into `.novel/bible.md` only after user confirmation when it affects canon.

## Verification Checklist

After implementing or modifying integration:

- [ ] Plugin imports cleanly with `python -m py_compile` or equivalent.
- [ ] Tool registration shows all expected names.
- [ ] OpenViking MCP `tools/list` or a simple tool call succeeds.
- [ ] `openviking_archive` writes a test record and returns a `viking://.../archives/...md` URI.
- [ ] `openviking_grep` can find a unique marker in that archived record.
- [ ] `openviking_read` can read the generated URI and show frontmatter + content.
- [ ] Secret rejection path was tested with a fake token and refused.
- [ ] Hermes native memory provider was not changed unless the user explicitly requested it.
- [ ] User is told that newly enabled plugins may require a new session/restart/reset to appear in the model-facing tool list.

## Common Pitfalls

1. **Exposing raw write/edit/forget directly.** Prefer a constrained wrapper. Raw deletion and broad edits should require explicit foreground confirmation.

2. **Treating OpenViking as the only source of truth.** In code projects, project files and `.agents/` state remain authoritative. In novels, `.novel/bible.md` remains authoritative.

3. **Saving everything.** OpenViking gets noisy if every chat turn is archived. Save decisions, handoffs, validation evidence, canon facts, and durable troubleshooting conclusions.

4. **Assuming JSON-only MCP responses.** OpenViking may return `text/event-stream`; parse SSE `data:` messages.

5. **Assuming a session header is always returned.** Some deployments may not provide `mcp-session-id`. Keep the client tolerant.

6. **Forgetting plugin lifecycle.** `hermes plugins enable ...` often takes effect on the next session. Verify by direct import if necessary, then tell the user restart/reset may be needed for model-facing tool visibility.

7. **Archiving secrets by accident.** Always scan content for common token/password shapes before writing.

## Reference Files

- `references/controlled-archive-session.md` — condensed implementation details and verification transcript from the validated Hermes default + OpenViking integration session.
