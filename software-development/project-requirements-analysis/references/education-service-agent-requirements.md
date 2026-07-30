# Education Service AI Agent Requirements Bundle — Example Synthesis

This reference captures a reusable pattern discovered from a Chinese education-service requirements folder. Use it as an example shape, not as a fixed project template.

## Folder Pattern

A requirements bundle may contain:

- `客户需求表.xlsx` — central feature list, development plan, module breakdown.
- `sql设计草稿.txt` — draft relational schema.
- `公司信息/*.docx`, `公司业务/*.docx`, `留学政策/*.docx` — RAG knowledge-base sources.
- `用户画像研判规则/*.docx` — rule base for lead qualification.
- `测试简历/*.pdf` — sample unstructured inputs for extraction and matching.
- `答辩须知.md`, `答辩所需文本交付物清单.txt` — delivery/acceptance constraints.

## Typical System Inference

This kind of bundle often describes a multi-role AI Agent system rather than a ready codebase:

1. Customer-service Agent
   - Company info Q&A
   - Business/project inquiry
   - Study-abroad policy Q&A
   - Project/course recommendation
   - Event/lecture registration
   - FAQ and light chat

2. Customer profile / lead qualification Agent
   - Accepts text, PDF resume, Excel, or Word customer info.
   - Applies explicit user-profile rules.
   - Outputs matched project, reasons, missing data, risks, and follow-up script.

3. Enterprise employee Agent
   - Lead CRUD and status updates.
   - Natural-language customer queries.
   - Oral daily report structuring.
   - Manager report lookup.
   - New-employee guide / organization Q&A.

4. Student assistant Agent
   - Leave/admin service workflow.
   - Complaint feedback ticketing.
   - Psychological care and risk alerts.
   - Academic/exam deadline query and reminders.
   - Application progress tracking.
   - Overseas life support RAG.

5. Intelligent reports
   - Customer operation analysis.
   - Daily/weekly employee report summary.
   - Student mental-health weekly report.
   - Complaint handling weekly report.

## Data Model Pattern

Common tables:

- `sys_user` — unified users and roles.
- `crm_lead` — leads and follow-up status.
- `employee_daily_report` — staff reports.
- `student_admin_service` — leave/exam/admin requests.
- `student_psych_profile` — long-term emotion profile.
- `student_psych_alert` — high-risk alerts.
- `student_feedback_ticket` — complaints and handling state.
- `student_score` — scores.
- `course_project` — courses/projects.
- `event_lecture`, `event_registration` — events and signups.

Engineer recommendations usually include adding foreign keys, RBAC tables, notification table, audit log, knowledge-document/chunk tables, academic-event table, and application-progress table.

## Good MVP for Demo / Defense

Prioritize three demonstrable loops:

1. Customer asks a question → RAG answer + project recommendation.
2. Input customer text/resume → profile qualification result.
3. Employee natural language command → query/update CRM or generate summary.

Secondary demo loops:

- Student submits leave/complaint → database ticket → teacher approval/update.
- Generate a simple customer or daily-report summary.

## Output Style for Chinese User

Use concise Chinese, tables, and code/architecture blocks. State conclusions early:

> “这不是一个已有完整代码项目，而是一个教育服务 AI Agent 系统的需求资料目录。”

Then provide modules, roles, database, architecture, and MVP priority.
