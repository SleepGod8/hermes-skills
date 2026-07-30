# Dify 1.16 Graph Patching Reference

Use when a local self-hosted Dify app has workflow graph/provider incompatibilities and the console cannot repair it cleanly.

## Read Graphs Safely

Large `workflows.graph` JSON often contains newlines and quotes. Avoid parsing raw `psql` text in the host shell. Prefer a Python script running in `docker-api-1` with `psycopg2`, using Dify container env vars:

```python
import os, psycopg2
conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'db_postgres'),
    port=int(os.getenv('DB_PORT', '5432')),
    dbname=os.getenv('DB_DATABASE', 'dify'),
    user=os.getenv('DB_USERNAME', 'postgres'),
    password=os.getenv('DB_PASSWORD', ''),
)
```

Copy scripts in and run:

```bash
docker cp scripts/patch_dify_models.py docker-api-1:/tmp/patch_dify_models.py
docker exec docker-api-1 python /tmp/patch_dify_models.py
```

Do not print env vars or DB passwords.

## Model Locations In Workflow Graph

Patch at least these shapes:

```python
# Standard LLM / classifier / parameter-extractor nodes
node['data']['model']

# Agent nodes
node['data']['agent_parameters']['model']['value']
```

Target built-in DeepSeek shape used successfully:

```python
TARGET_PROVIDER = 'langgenius/deepseek/deepseek'
TARGET_MODEL = 'deepseek-v4-flash'
TARGET_MODE = 'chat'
```

For objects with `name`, update `name`; for objects with `model`, update `model`. Preserve or set `completion_params.temperature`.

## Verification Pattern

A useful verifier walks all nodes and reports incompatible entries:

```python
bad = []
for node in graph.get('nodes', []):
    data = node.get('data') or {}
    candidates = []
    if isinstance(data.get('model'), dict):
        candidates.append(('model', data['model']))
    agent_model = (((data.get('agent_parameters') or {}).get('model') or {}).get('value'))
    if isinstance(agent_model, dict):
        candidates.append(('agent_parameters.model.value', agent_model))
    for path, model in candidates:
        provider = model.get('provider')
        name = model.get('name') or model.get('model')
        if provider != TARGET_PROVIDER or name != TARGET_MODEL:
            bad.append({'node_id': node.get('id'), 'title': data.get('title'), 'path': path, 'provider': provider, 'name': name})
print({'model_count': model_count, 'bad_count': len(bad), 'bad': bad})
```

Expected success for exact migration tasks: `bad_count=0` per affected workflow.

## Console Validation Pitfalls

- `conversation_variables` and `rag_pipeline_variables` should be serialized object storage (`{}`) for empty values. `[]` can make Dify 1.16 console Pydantic response validation fail.
- Normal workflow `kind` should be `standard`. Legacy/custom `basic` can make runtime reject execution.
- Dependency extraction errors like `LLMNodeData prompt_template Field required` or `KnowledgeRetrievalNodeData multiple_retrieval_config` usually point to malformed imported DSL nodes. They are separate from provider/model migration and should be debugged at node schema level.
- For `KnowledgeRetrievalNodeData`, Dify 1.16 expects `multiple_retrieval_config.score_threshold` to be numeric and `reranking_mode` to be a string. Legacy DSLs may store `score_threshold` as `{enabled,value}` and `reranking_mode` as a rerank-model object.
- If `reranking_enable=false`, avoid `reranking_mode='reranking_model'` with an empty model object. The console can still require `Rerank 模型`. Set `reranking_mode='weighted_score'`, `reranking_model=null`, and include `weights` to avoid the checklist error while keeping rerank disabled.

Known-good no-rerank retrieval config:

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

## Knowledge Base Import Failure Signature

If worker logs show embedding `429 Throttling.RateQuota`, the problem is rate limiting from the embedding provider. Reduce import batch/segments or change embedding provider; do not chase file parsing unless logs show parser errors.
