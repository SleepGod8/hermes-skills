# Dify Workflow Adapter Pattern for FastAPI AI Features

Use this when a FastAPI prototype has rule-based "AI" features and the user asks to implement them through Dify workflows.

## Durable Pattern

1. Keep existing rule/FAQ/template behavior as fallback so tests and demos still run without credentials.
2. Add lightweight dotenv loading early in config so PyCharm/uvicorn picks up project-local `.env` without manual `export`.
3. Dify 1.16 self-hosted Service API uses an App API Key for a Workflow App. Prefer per-capability App API Key env vars:
   - `DIFY_ENABLED`
   - `DIFY_BASE_URL`
   - `DIFY_API_KEY` as optional shared fallback
   - `DIFY_INTENT_API_KEY`
   - `DIFY_RAG_API_KEY`
   - `DIFY_JUDGMENT_API_KEY`
   - `DIFY_SUMMARY_API_KEY`
   - `DIFY_NL2SQL_API_KEY`
   - `DIFY_REPORT_API_KEY`
   - `DIFY_PSYCH_API_KEY`
4. Add a small client wrapper around Dify Service API:
   - `POST {DIFY_BASE_URL}/workflows/run`
   - `Authorization: Bearer app-...`
   - `response_mode: blocking`
   - `inputs: {...}`
   - `user: <stable app user id>`
   - Optionally call `/workflows/{workflow_id}/run` only when intentionally targeting a specific published workflow version.
5. Make the wrapper return `None` when disabled, unconfigured, timed out, HTTP-failed, or malformed. Service functions then fall back locally.
6. Integrate Dify at the service boundary, not directly in routes. Routes should continue orchestrating DB transactions, notifications, audit logs, and response models.
7. Parse Dify outputs defensively. Workflow outputs may be a dict under `data.outputs`, or a `text` string containing JSON. Strip Markdown fences and `<think>...</think>` before `json.loads`.
8. For NL2SQL, Dify may propose SQL, but backend must still enforce:
   - statement starts with `SELECT`
   - no dangerous SQL keywords
   - allowed tables only when practical
   - mask sensitive fields before returning rows.
9. For RAG/chat, pass local search hits as workflow context. If Dify answers, return its answer and sources; otherwise use local knowledge search.
10. For customer judgment/recommendation, use Dify output only to enhance structured fields, scores, reasons, risks, and scripts. Keep CRM writes and judgment/audit records owned by backend code.
11. Safety-critical flows such as psychological risk detection need local safety overrides. If Dify returns low/no risk but local high-risk keywords match, trigger the backend alert anyway.
12. Tests should cover both Dify-enabled and fallback behavior where possible; avoid making unit tests dependent on public network credentials.

## Workflow Capability Map Example

| Capability | Env var |
|---|---|
| Intent recognition | `DIFY_INTENT_API_KEY` |
| RAG answer | `DIFY_RAG_API_KEY` |
| Customer extraction/judgment/recommendation | `DIFY_JUDGMENT_API_KEY` |
| Summary | `DIFY_SUMMARY_API_KEY` |
| NL2SQL | `DIFY_NL2SQL_API_KEY` |
| Report generation | `DIFY_REPORT_API_KEY` |
| Psychological risk detection | `DIFY_PSYCH_API_KEY` |

## Dify DB/Workflow Creation Pitfalls

Prefer Dify console/API import when authenticated. If a local self-hosted Dify instance must be bootstrapped directly for a prototype, be careful:

- `workflows.kind` must be `standard` in Dify 1.16; `basic` causes `invalid workflow kind value basic`.
- Workflow apps need a published workflow: create/update both draft and published workflow records, and set `apps.workflow_id` to the published workflow id.
- `api_tokens.type` must be `app`, and `apps.enable_api` must be true.
- Avoid `memory.query_prompt_template` references such as `{{#sys.query#}}` in a pure Workflow App unless that variable exists. A bad reference causes runtime failure like `Variable #sys.query# not found`.
- Validate against `/v1/workflows/run` before wiring the app into FastAPI.
- Dify console `WorkflowResponse conversation_variables Field required` usually means direct DB-inserted workflow variable storage has the wrong shape. In Dify 1.16, `conversation_variables` and `rag_pipeline_variables` should be serialized object maps like `{}`, not list literals like `[]`; the model property calls `.values()` before building variable responses.

## Verification

Run full tests, then run real HTTP probes against representative endpoints after restarting the dev server.

Direct Dify probe pattern:

```python
from pathlib import Path
import httpx

env = dict(line.split("=", 1) for line in Path(".env").read_text(encoding="utf-8").splitlines() if "=" in line and not line.startswith("#"))
r = httpx.post(
    env["DIFY_BASE_URL"].rstrip("/") + "/workflows/run",
    headers={"Authorization": "Bearer " + env["DIFY_API_KEY"]},
    json={"inputs": {"task": "intent", "text": "粤教服务的使命是什么"}, "response_mode": "blocking", "user": "verify"},
    timeout=90,
)
print(r.status_code, r.json().get("data", {}).get("status"))
```

Expected result: HTTP 200 and workflow status `succeeded`. If real Dify credentials are unavailable, report that the Dify path is implemented but only fallback behavior was exercised.
