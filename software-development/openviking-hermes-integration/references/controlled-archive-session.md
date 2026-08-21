# Controlled Archive Session Notes

## Context

A local OpenViking MCP server was already running at `http://127.0.0.1:1933` with configuration under the user's workspace. Hermes default needed safe OpenViking access without replacing Hermes native memory.

## Implemented Tool Shape

The validated Hermes plugin exposed:

```text
openviking_find     -> OpenViking raw `find`, read-only semantic retrieval
openviking_grep     -> OpenViking raw `grep`, read-only exact/regex search
openviking_read     -> OpenViking raw `read`, read-only URI reading
openviking_archive  -> controlled wrapper around OpenViking raw `write`
```

`openviking_archive` writes only structured Markdown records under:

```text
viking://user/master/archives/<workspace>/<category>/<YYYYMMDD>-<title-slug>-<hash>.md
```

It uses `mode=create` to avoid overwrites.

## Validated MCP Details

MCP endpoint:

```text
http://127.0.0.1:1933/mcp
```

Headers used successfully:

```text
Content-Type: application/json
Accept: application/json, text/event-stream
MCP-Protocol-Version: 2025-06-18
Authorization: Bearer <root_api_key>
X-OpenViking-Account: local
X-OpenViking-User: master
X-OpenViking-Actor-Peer: hermes-default-readonly-tools
```

Observed OpenViking server version in the successful session:

```text
openviking 1.27.0
```

Observed raw tools included:

```text
find, search, read, list, tree, remember, write, edit,
add_resource, list_watches, cancel_watch, grep, glob, forget, health
```

The Hermes-facing plugin deliberately exposed only safe wrappers, not the full raw tool list.

## Verification Transcript Summary

After adding `openviking_archive`, direct plugin import registered:

```text
REGISTERED openviking_find,openviking_grep,openviking_read,openviking_archive
```

A unique test marker was archived:

```text
OVARCHIVE_TEST_20260821_controlled_archive
```

Archive result shape:

```json
{
  "ok": true,
  "rawTool": "write",
  "uri": "viking://user/master/archives/hermes-openviking-test/decision/20260821-controlled-archive-test-ovarchive_test_20260821-3257590011.md",
  "workspace": "hermes-openviking-test",
  "category": "decision",
  "status": "approved",
  "message": "Wrote 808 bytes ... Indexing: semantic=complete, vector=complete."
}
```

Then `openviking_grep` found the marker under `viking://user/master/archives`, and `openviking_read` read back the generated Markdown with frontmatter.

A fake secret payload was rejected:

```text
archive content appears to contain secrets/tokens; refuse to write
```

Hermes native memory provider remained unset/unchanged:

```text
MEMORY_PROVIDER None
```

## Implementation Notes

- Parse both JSON and `text/event-stream` MCP responses.
- Do not assume `mcp-session-id` is present in responses.
- Load the OpenViking root API key from the local OpenViking config only when present.
- Keep plugin availability tolerant: the root health endpoint may not be the authoritative readiness check.
- Tell the user that `hermes plugins enable` may require a new session/restart/reset for the model-facing tool list to refresh.

## Safety Rules for Future Edits

- Do not expose raw `write`, `edit`, `forget`, or `remember` unless the user explicitly asks for unrestricted access and understands the risk.
- Keep `openviking_archive` append-like by creating new records; avoid silent rewrites.
- Keep archive content scoped to durable decisions, handoffs, validation evidence, canon, review findings, and troubleshooting conclusions.
- Reject likely credentials before writing.
