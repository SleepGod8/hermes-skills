# Dify 1.16 Workflow App Key Integration Notes

Use when integrating a FastAPI project with self-hosted Dify 1.16 workflows.

## Durable Lessons

- Dify 1.16 Service API usually uses one `app-*` API key per Workflow App. Calling `POST /v1/workflows/run` with that key runs the app's default published workflow.
- Avoid designing project config as one global `DIFY_API_KEY` plus multiple `DIFY_WORKFLOW_*` IDs unless the deployment explicitly supports version-specific workflow execution.
- Recommended project env shape:
  - `DIFY_ENABLED=true`
  - `DIFY_BASE_URL=http://localhost/v1`
  - `DIFY_<SCENE>_API_KEY=app-...` for `INTENT`, `RAG`, `JUDGMENT`, `SUMMARY`, `NL2SQL`, `REPORT`, `PSYCH`
  - Optional version IDs only for special cases: `DIFY_WORKFLOW_<SCENE>`.

## Programmatic Workflow Creation Pitfalls

If bypassing the Dify console and inserting workflow rows directly, validate both Service API execution and console readability.

Known fields for Dify 1.16:

- `workflows.kind` must be `standard` for normal apps, not `basic`.
- `workflows.conversation_variables` should be serialized object JSON, usually `{}` when empty. `[]` can make console `WorkflowResponse` validation fail.
- `workflows.rag_pipeline_variables` should also be `{}` when empty.
- Avoid generated node configs that reference missing variables such as `#sys.query#`; use only Start node variables unless the graph actually provides system variables.
- Published workflow must exist and `apps.workflow_id` should point at it.
- `apps.enable_api=true` and a row in `api_tokens` with `type='app'` are required for Service API access.

## Output Parsing

LLM nodes may return a single `outputs.text` string even when asked for JSON. Client adapters should:

1. Read `data.outputs` from the Service API response.
2. If it is a string, strip Markdown code fences.
3. Strip reasoning tags such as `<think>...</think>` before JSON parsing.
4. Fall back to `{ "text": raw, "answer": raw }` if parsing fails.

## Safety Pattern

Dify output should enhance business decisions, not own side effects.

- Keep database writes, CRM creation, audit logs, notifications, and status transitions in FastAPI service code.
- Keep NL2SQL behind backend checks: only `SELECT`, allowed table whitelist, no direct execution of model-provided mutations.
- For safety-critical domains like psychological risk, use backend high-risk keyword rules as a mandatory override if the model under-classifies risk.

## Verification Checklist

- Direct Dify call: `POST /v1/workflows/run` returns HTTP 200 and `data.status == 'succeeded'`.
- Dify console can open the app workflow page without Pydantic validation toast errors.
- FastAPI tests pass with Dify enabled and with Dify disabled/fallback where applicable.
- Runtime probes cover at least: chat, judgment, NL2SQL, psych high-risk, report.
