---
name: dify-workflow-ops
description: Operate and troubleshoot self-hosted Dify apps/workflows/knowledge bases from Docker and Postgres, including model migration, workflow graph patching, and safe verification.
version: 1.0.0
author: agent
license: MIT
tags: [dify, workflow, chatflow, knowledge-base, docker, postgres, model-migration]
---

# Dify Workflow Ops

Use this skill when configuring, repairing, or verifying a self-hosted Dify workspace, especially when the user asks about Workflow/Chatflow apps, knowledge-base import failures, app API keys, or model/provider migration.

## Core Principles

1. Treat Dify console/API keys, provider credentials, database passwords, and tokens as secrets. Never print them; redact logs before summarizing.
2. Prefer Dify console/API for normal setup. Direct database edits are a recovery path for local self-hosted Dify when the user explicitly asks to fix a local instance and the change is narrow.
3. Distinguish Dify Service API keys from workflow IDs. Dify 1.16 Service API uses each app's API key for `/v1/workflows/run`; a global key plus workflow ID is usually the wrong model.
4. For any graph/database edit, verify both structure and runtime: inspect graph nodes, run the workflow/API when possible, and check worker/API logs.

## Discovery Checklist

```bash
docker ps --format '{{.Names}}\t{{.Image}}\t{{.Status}}' | grep -E 'dify|docker-'
docker exec docker-db_postgres-1 psql -U postgres -d dify -c "select id, name, mode, workflow_id from apps order by updated_at desc limit 20;"
docker exec docker-db_postgres-1 psql -U postgres -d dify -c "select provider_name, model_name, model_type from tenant_default_models order by model_type;"
docker exec docker-db_postgres-1 psql -U postgres -d dify -c "select provider_name, credential_name from provider_credentials order by created_at;"
```

Redact env/log output before showing it:

```bash
docker logs --tail 200 docker-worker-1 2>&1 | sed -E 's/(api[_-]?key|token|password|secret|authorization)([^A-Za-z0-9_:-]*[:=][^[:space:]]+)/\1=[REDACTED]/Ig'
```

## Common Fixes

### Knowledge Base Import Fails

Check `docker-worker-1` first. If the log shows `status_code: 429`, `Throttling.RateQuota`, or `Response output is missing or does not contain embeddings`, the failure is usually embedding provider rate limit, not a bad document.

Actions:
- Wait and retry failed indexing after quota recovers.
- Import fewer documents per batch.
- Increase chunk size / reduce segment count.
- Switch to a higher-quota or local embedding model.

### Dify Console Cannot Open Workflow

If the console reports `WorkflowResponse conversation_variables Field required`, check workflow serialized variable columns. Dify 1.16 expects object-shaped serialized storage for some columns.

```sql
update workflows
set conversation_variables='{}', rag_pipeline_variables='{}'
where app_id='<app_id>';
```

Also ensure `kind='standard'` for normal workflows, not legacy values like `basic`.

### Change Incompatible LLM Nodes To Integrated Provider

For Chatflow/Workflow app graphs, patch every node with `data.model` and agent node model references such as `data.agent_parameters.model.value`. For Dify's built-in DeepSeek integration, a working shape is:

```json
{
  "provider": "langgenius/deepseek/deepseek",
  "name": "deepseek-v4-flash",
  "mode": "chat",
  "completion_params": {"temperature": 0.4}
}
```

After patching, verify no incompatible provider/model remains.

### Fix Knowledge Retrieval Node Checklist Errors

Dify 1.16 validates `KnowledgeRetrievalNodeData.multiple_retrieval_config` strictly. If a Chatflow checklist says `score_threshold` or `reranking_mode` is invalid, convert legacy object fields to scalar values.

If the user does **not** want/need a Rerank model, do not set `reranking_mode` to `reranking_model` with an empty model object; the console may then show `Rerank 模型 不能为空`. Use `weighted_score`, disable rerank, and keep `reranking_model` null:

```json
{
  "reranking_enable": false,
  "reranking_model": null,
  "top_k": 4,
  "score_threshold_enabled": false,
  "score_threshold": 0,
  "reranking_mode": "weighted_score",
  "weights": {
    "vector_setting": {"vector_weight": 1.0, "embedding_provider_name": "", "embedding_model_name": ""},
    "keyword_setting": {"keyword_weight": 0.0}
  }
}
```

Verify with Dify's own Pydantic entity inside the API container, using the venv Python and `PYTHONPATH=/app/api`:

```bash
docker exec docker-api-1 sh -lc 'cd /app/api && PYTHONPATH=/app/api /app/api/.venv/bin/python /tmp/validate_kr.py'
```

## Verification

1. Query the affected apps and workflows by exact app name.
2. Parse workflow graph JSON with Python inside the Dify API container or via safe DB access; avoid `psql` text parsing for large JSON because wrapping/truncation can corrupt reads.
3. Count model nodes and report `bad_count=0` for target provider/model checks.
4. Check recent API logs for validation errors.
5. If the app has an API key, call `/v1/workflows/run` with a harmless prompt and confirm HTTP 200 plus `data.status=succeeded`.

## Reference

See `references/dify-graph-patching.md` for reusable Python snippets and pitfalls from Dify 1.16 graph/model repairs.
