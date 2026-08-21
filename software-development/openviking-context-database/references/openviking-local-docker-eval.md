# OpenViking local Docker evaluation notes

Session-derived notes for validating OpenViking as a shared context DB before switching Hermes or DSH memory providers.

## Validated local shape

- Run OpenViking independently from Hermes' Python environment.
- Official image used successfully: `ghcr.io/volcengine/openviking:latest`.
- Windows workspace mount pattern: `E:/Hermes workspace/openviking-data:/app/.openviking`.
- First validation disabled the built-in bot with `OPENVIKING_WITH_BOT=0`.
- Host Ollama from Docker was reachable at `http://host.docker.internal:11434`.
- `bge-m3:latest` embedding worked when configured with dimension `1024`.
- Basic endpoints to verify: `/health`, `/ready`, `/studio`.

## Authentication lesson

In `api_key` mode, a configured `root_api_key` can protect the service but may be rejected by tenant-scoped data APIs with:

```text
ROOT API keys cannot access tenant-scoped data APIs in api_key mode. Use a user/admin API key for data access, or trusted mode for upstream identity assertion.
```

For local-only evaluation, `trusted` mode with explicit `account` and `user` worked. A normal user/admin key is the cleaner production approach.

`actor_peer_id` must be alphanumeric; values containing punctuation such as `agent:hermes-default` can fail validation.

## Docker CLI lesson

The container image can contain `ov` at `/app/.venv/bin/ov` without exposing it on PATH. Use:

```bash
docker exec openviking sh -lc 'export PATH=/app/.venv/bin:$PATH; ov --help'
```

If the CLI asks for a display language, run:

```bash
ov language zh-CN
```

## Smoke test

A minimal data-plane smoke test that exercised write/read/find:

```bash
ov mkdir viking://resources -o json
ov write viking://resources/hello.md --content "OpenViking local Docker smoke test" --mode create --wait -o json
ov read viking://resources/hello.md -o json
ov find "本地部署验证" -o json
```

Successful semantic search returned the test resource, proving storage, embedding, indexing, and retrieval were connected.

## Import and retrieval evaluation

Before switching any memory provider, import a few project docs and evaluate three modes separately:

```bash
ov add-resource /path/to/docs --parent-auto-create viking://resources/eval/project --include "*.md" --ignore-dirs ".git,node_modules,__pycache__,third_party" --tag project=eval --wait --timeout 300 -o json
ov tree viking://resources/eval/project -L 4 -n 80 -o json
ov grep root_api_key -u viking://resources/eval/project -n 8 -o json
ov find "trusted 模式 account user header" -u viking://resources/eval/project -n 8 -o json
```

Observed behavior:

- `tree` is useful for hierarchy and directory abstracts, but Markdown chunking can generate ugly URIs.
- `grep` is the strongest tool for exact config fields, headers, endpoint paths, and error strings.
- `find` is useful for concept queries such as authentication, client configuration, and deployment patterns; validate important results with `read`/`grep`.
- Slow semantic summarization can cause CLI `--wait` timeouts while the service remains healthy and partial retrieval is already usable. Check `ov task list -o json` and `ov status -o json` before calling an import failed.

## Reporting recommendation

When reporting to the user, state explicitly that Hermes memory provider was not changed, list imported corpora and `viking://` roots, summarize health/vector/task state, and score `tree`, `grep`, and `find` separately.
