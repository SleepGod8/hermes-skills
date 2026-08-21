# OpenViking local Docker deployment (Windows, 2026-08)

Use this reference when the user asks to run OpenViking locally via Docker on the Windows Hermes workstation.

## Working deployment shape

Host data directory:

```text
E:/Hermes workspace/openviking-data
```

Files under that directory are mounted to `/app/.openviking` in the container:

```bash
mkdir -p "E:/Hermes workspace/openviking-data/data"
docker rm -f openviking openviking-caddy >/dev/null 2>&1 || true
docker run -d \
  --name openviking \
  -p 1933:1933 \
  --add-host=host.docker.internal:host-gateway \
  -v "E:/Hermes workspace/openviking-data:/app/.openviking" \
  -e OPENVIKING_WITH_BOT=0 \
  -e OPENVIKING_SERVER_PORT=1933 \
  --restart unless-stopped \
  ghcr.io/volcengine/openviking:latest
```

`OPENVIKING_WITH_BOT=0` keeps this as a clean context DB service and avoids starting VikingBot.

## Known-good `ov.conf`

For local testing, prefer `trusted` mode with explicit identity headers/config. In `api_key` mode, using only `server.root_api_key` makes health checks pass but tenant-scoped data APIs fail with:

```text
ROOT API keys cannot access tenant-scoped data APIs in api_key mode.
```

Known-good local config, using host Ollama from inside Docker:

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 1933,
    "auth_mode": "trusted",
    "root_api_key": "local-dev-openviking-key",
    "cors_origins": ["*"]
  },
  "storage": {
    "workspace": "/app/.openviking/data",
    "vectordb": { "name": "context", "backend": "local" },
    "agfs": { "backend": "local" }
  },
  "embedding": {
    "dense": {
      "provider": "litellm",
      "api_base": "http://host.docker.internal:11434",
      "model": "ollama/bge-m3:latest",
      "dimension": 1024,
      "input": "text"
    }
  },
  "vlm": {
    "provider": "litellm",
    "api_key": "ollama",
    "api_base": "http://host.docker.internal:11434",
    "model": "ollama/llama3.2:3b"
  }
}
```

Known-good `ovcli.conf`:

```json
{
  "url": "http://127.0.0.1:1933",
  "root_api_key": "local-dev-openviking-key",
  "account": "local",
  "user": "master",
  "actor_peer_id": "hermesdefault"
}
```

`actor_peer_id` must be an alphanumeric string. Values like `agent:hermes-default` can fail with `Invalid peer_id: peer_id must be alpha_numeric string`.

## Verification sequence

1. Health check should show the service is up:

```bash
curl -s http://127.0.0.1:1933/health
# {"status":"ok","healthy":true,"version":"v0.4.15","auth_mode":"trusted"}
```

2. Ready check should verify storage, vectordb, embedding, and Ollama:

```bash
curl -s -H 'X-API-Key: local-dev-openviking-key' \
  -H 'X-OpenViking-Account: local' \
  -H 'X-OpenViking-User: master' \
  http://127.0.0.1:1933/ready
```

Expected checks include:

```json
{"vectordb":"ok","api_key_manager":"ok","embedding":"ok","ollama":"ok"}
```

3. CLI inside the container needs PATH and a display language set once:

```bash
docker exec openviking sh -lc 'export PATH=/app/.venv/bin:$PATH; ov language zh-CN'
```

4. Root `viking://` may 404 before namespaces are created. Create `resources`, then write/read/find a smoke-test file:

```bash
docker exec openviking sh -lc 'export PATH=/app/.venv/bin:$PATH; \
  ov mkdir viking://resources -o json || true; \
  ov write viking://resources/hello.md \
    --content "OpenViking local Docker smoke test. 主人本地部署验证。" \
    --mode create --wait -o json; \
  ov read viking://resources/hello.md -o json; \
  ov find "本地部署验证" -o json'
```

A successful smoke test returns the file content and `ov find` returns `viking://resources/hello.md` with a nonzero score.

## Pitfalls

- `openviking-server` and `ov` are in `/app/.venv/bin`; if `docker exec` says command not found, export `PATH=/app/.venv/bin:$PATH`.
- `/health` can be OK while `/ready` exposes embedding/provider problems; check both before declaring the service usable.
- The first Ollama `bge-m3` embedding calls can take ~8–12 seconds but still succeed; use `/ready` and a write/read/find smoke test rather than judging by slow-call warnings alone.
- If Docker daemon is not running, start Docker Desktop first as in the main skill, then rerun the container command.
