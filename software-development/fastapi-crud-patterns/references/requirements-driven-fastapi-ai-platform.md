# Requirements-Driven FastAPI AI Platform Alignment

Use this reference when a simple FastAPI prototype must be brought closer to a developer requirements specification for an AI/business workflow platform.

## Pattern

1. Read the requirements document and current code side by side.
2. Identify gaps that affect future extensibility and traceability, not just visible demo flows.
3. Prefer small compatible additions over broad rewrites:
   - Add missing ORM tables.
   - Add Pydantic DTOs.
   - Add focused endpoints.
   - Keep existing response shapes stable unless the user asks for a breaking API redesign.
4. Add tests for each new requirement-backed behavior.
5. Run `pytest` and restart/probe the service if it is already running.

## Common Requirement Gaps

For AI/Agent education-service platforms, requirement docs often demand traceability that prototypes skip:

- `customer_info_source`: preserve raw uploaded/text customer data plus extracted JSON.
- `judgment_record`: preserve match score, recommended project, reasons, risks, follow-up script, source id, lead id, operator.
- `knowledge_chunk`: store document chunks for RAG-like retrieval even before a vector DB exists.
- `operation_log`: record customer status changes, approvals, complaint handling, psychological alert follow-up.
- `notification`: record system/teacher/student notifications when email/SMS is not yet configured.

## Endpoint Backfill Examples

- `POST /api/judgment/text`: standard requirement-facing alias for existing text judgment.
- `GET /api/judgment/{id}` and `GET /api/judgment-records`: audit/readback for judgment results.
- `GET /api/customer-sources`: inspect parsed source records.
- `GET /api/knowledge/search?q=...`: local keyword/chunk search as a mock RAG layer.
- `PATCH /api/feedback/{ticket_id}`: complaint handling and student notification.
- `GET /api/psych/alerts`, `PATCH /api/psych/alerts/{alert_id}`: teacher follow-up and alert resolution.

## Pitfalls

- Chinese search strings like `新加坡学费` may be treated as one token by a naive regex. Add domain terms (`新加坡`, `德国`, `学费`, `签证`, `报名`, `双元制`, `APS`, `B1`, etc.) and extract those from the query.
- If a database file already exists, `create_all()` will not add new columns to existing tables; for new tables it is fine. If changing existing table schemas, use migrations or reset only with user approval.
- Do not claim real LLM integration when implementing rules/mock RAG. Label it as rule/mock and keep a future adapter boundary.
- After editing code while a uvicorn process is running, kill/restart it before HTTP probing so requests hit the new code.
