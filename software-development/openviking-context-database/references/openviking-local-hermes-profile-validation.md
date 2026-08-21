# OpenViking local Docker + Hermes profile validation (2026-08)

Use this reference with `openviking-context-database` when the user asks to run or validate OpenViking as a Hermes/DSH shared project context store. This is session-specific detail; keep the main SKILL.md class-level.

## Working local deployment

- Docker container: `openviking`
- Image: `ghcr.io/volcengine/openviking:latest`
- Service version observed: `v0.4.15`
- Host URL: `http://127.0.0.1:1933`
- Studio: `http://127.0.0.1:1933/studio`
- Host data dir: `E:/Hermes workspace/openviking-data`
- Container data dir: `/app/.openviking`
- Auth mode for local testing: `trusted` with local root key still configured
- Embedding: `litellm` → `ollama/bge-m3:latest`, dimension `1024`, via `http://host.docker.internal:11434`
- VLM / semantic summary: `openai` → ASLNetPlus endpoint `https://api.aslnet.cloud/v1`, model `gpt-5.4`

Health checks:

```bash
curl -s http://127.0.0.1:1933/health
curl -s \
  -H 'X-API-Key: <local-root-key>' \
  -H 'X-OpenViking-Account: local' \
  -H 'X-OpenViking-User: master' \
  http://127.0.0.1:1933/ready
```

Container CLI:

```bash
docker exec openviking sh -lc 'export PATH=/app/.venv/bin:$PATH; ov status'
```

## Important behavior discovered

- In `api_key` mode, the root key cannot access tenant-scoped data APIs. It returns: `ROOT API keys cannot access tenant-scoped data APIs in api_key mode...`. For local testing, either create user/admin keys or use trusted mode with asserted account/user headers.
- `actor_peer_id` must be alphanumeric for the CLI; `agent:hermes-default` failed, `hermesdefault` worked.
- Container shell does not expose `ov` on PATH by default; use `export PATH=/app/.venv/bin:$PATH`.
- `ov find` / `ov tree` may prefix JSON output with `cmd: ...`; helper scripts should strip to the first JSON character.
- `ov wait` and `--wait` can hit HTTP request timeouts even when the background task eventually completes. Verify with `ov task list`, `ov status`, `ov tree`, `ov find`, and `ov read` before declaring failure.
- `tree` structure is useful; overview/abstract generation can lag and show `[Directory overview is not generated]`.
- `grep` is best for exact fields/errors/headers; `find` is good for semantic recall but should be followed by `read` on top 5-8 results.

## Import / evaluation pattern

1. Import small batches first; do not switch Hermes default memory provider.
2. Validate `ov tree`, `ov grep`, `ov find`, then `ov read` on returned URIs.
3. For questions, use `find -> read -> synthesize`; for config fields, add `grep` terms.
4. Keep OpenViking for project docs / long references / cross-agent knowledge, not persona-critical short memories.

Validated helper:

```bash
python "C:/Users/80704/AppData/Local/hermes/skills/software-development/openviking-context-database/scripts/ov_context_query.py" \
  "DSH OpenClaw bridge 插件 能否接 OpenViking 共享记忆 需要哪些 header API" \
  --uri viking://resources/eval-small \
  --grep X-OpenViking-Account \
  --grep root_api_key \
  -n 3 \
  --read-chars 800
```

## Hermes test profile validation

Created profile:

```text
openvikingtest
```

Path:

```text
C:/Users/80704/AppData/Local/hermes/profiles/openvikingtest
```

Configuration:

```bash
hermes --profile openvikingtest config set memory.provider openviking
```

Profile `.env` values used:

```text
OPENVIKING_ENDPOINT=http://127.0.0.1:1933
OPENVIKING_API_KEY=<local root key>
OPENVIKING_ACCOUNT=local
OPENVIKING_USER=master
OPENVIKING_AGENT=hermestest
```

Status command:

```bash
hermes --profile openvikingtest memory status
```

Expected result:

```text
Provider:  openviking
Plugin:    installed ✓
Status:    available ✓
```

Direct tool validation command:

```bash
hermes --profile openvikingtest -z '请只使用 OpenViking 记忆插件自带的 viking_search 和 viking_read 工具，不要使用本地脚本。任务：在 viking://resources/eval-small 查找 Gateway API 的 X-OpenViking-Account / X-OpenViking-User header，并简短列出读到的 URI 和结论。'
```

Observed result: `viking_search` and `viking_read` worked directly after `OPENVIKING_API_KEY` was added. Without `OPENVIKING_API_KEY`, direct viking tools were rejected as `UNAUTHENTICATED` in this local trusted+root-key setup, even though the fallback Docker CLI helper could query successfully.

Do not apply this to the default profile until the user explicitly asks. The default profile contains persona-critical built-in memory and should not be used as the first provider-switch target.
