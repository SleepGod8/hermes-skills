# FastAPI Prototype Frontend Template Preview Pattern

Use this when the user asks to find/adapt a frontend template for a FastAPI prototype and wants to see the effect before replacing the current UI.

## Durable Pattern

1. Inspect the current static frontend and backend routing first. In simple FastAPI prototypes, `app/static/index.html` plus a root `HTMLResponse` route is common.
2. Choose a template class that matches the domain and workflow. For operational education/CRM/AI platforms, prefer dashboard/admin templates over marketing landing pages. Good references: SB Admin 2 / AdminLTE / Vuexy-style admin dashboards.
3. Do not overwrite the current homepage immediately. Create a preview artifact such as:
   - `app/static/template_preview.html`
   - `GET /template-preview`
4. Make the preview page call real backend APIs, not only static mock cards. At minimum wire:
   - dashboard metrics: `/api/dashboard`
   - AI/chat test: `/api/chat`
   - report preview: `/api/reports/customer`
5. Keep the first preview implementation low-risk: standalone HTML/CSS/JS, no build step, no npm dependency, no template migration across frameworks unless the user approves.
6. For management dashboards, use dense but readable layout: sidebar navigation, sticky topbar, metric cards, module cards, status panel, table/list panels, and one live API interaction panel.
7. Preserve old UI for comparison. Add a “返回旧版” action back to `/`.
8. Verify in three layers:
   - `python -m pytest -q`
   - restart uvicorn
   - browser navigation + screenshot/vision check for layout, overlap, blank areas, and live data
9. If the preview is accepted, then plan a second pass to replace `/` or split assets into CSS/JS modules. Do not do that in the first preview unless requested.

## User Preference Signal From Yuejiao Project

The user prefers seeing a working frontend effect first before a full replacement. For `D:\PythonProject\yuejiao`, create a template preview page and keep the existing homepage available for comparison.
