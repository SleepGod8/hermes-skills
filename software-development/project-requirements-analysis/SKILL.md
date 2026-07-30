---
name: project-requirements-analysis
description: "Analyze project requirements from codebases or document bundles and produce engineer-focused requirements reports."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [Requirements, Project Analysis, Documents, RAG, Architecture]
    related_skills: [codebase-inspection, ocr-and-documents, project-code-review]
---

# Project Requirements Analysis

Use this when the user asks to analyze a project’s requirements, business scope, functional modules, data model, or MVP plan — especially when the target folder contains documents rather than source code.

## Trigger Phrases

- “分析这个项目需求”
- “分析目录里的项目/资料/需求”
- “以资深代码工程师身份分析需求”
- “看这个文件夹要做什么系统”
- “帮我梳理功能模块 / 数据库 / API / 答辩方案”

## Workflow

1. **Classify the folder first**
   - Search for source files (`*.py`, `*.js`, `*.java`, `package.json`, `requirements.txt`, etc.).
   - Search for requirement artifacts (`*.docx`, `*.xlsx`, `*.pdf`, `*.md`, `*.txt`).
   - If there are few/no code files but many documents, explicitly state that this is a **requirements/document bundle**, not a finished code project.

2. **Extract the highest-signal documents**
   - Prefer `read_file` for `.txt`, `.md`, `.docx`, `.xlsx`, and text-based `.pdf` when available; Hermes can often extract document text directly.
   - For difficult local PDFs, follow `ocr-and-documents` and use PyMuPDF / OCR only when needed.
   - Prioritize files named like: `需求`, `客户需求`, `开发计划`, `数据库`, `SQL`, `规则`, `政策`, `公司信息`, `FAQ`, `答辩`.

3. **Build the requirements map**
   - Identify user roles / actors.
   - Extract major modules and subfeatures.
   - Map each feature to data tables, APIs, knowledge-base documents, and AI capabilities.
   - Identify business closed loops, not just isolated functions.
   - Distinguish MVP /答辩必做 from later enhancements.

4. **Engineer-focused output format**
   - Project nature and conclusion.
   - Core roles.
   - Functional modules table.
   - Data model / database analysis.
   - Recommended architecture.
   - MVP priority table.
   - Risks and missing requirements.
   - Demo / acceptance scenarios.

5. **Be concise but concrete**
   - Do not dump all extracted document text.
   - Quote only the few facts needed to support conclusions.
   - Use tables and short workflow diagrams when useful.

## Common Pitfalls

- Do **not** treat every folder as a codebase. If searches for code files are empty, pivot to document/requirements analysis.
- Do **not** stop after listing files; synthesize what system the files imply.
- Do **not** over-index on low-signal filler documents. Prioritize requirement spreadsheets, SQL drafts, user rules, FAQ, business docs, and answer-defense notes.
- When a folder mixes knowledge-base content and app requirements, separate **RAG corpus** from **transactional business data**.

## Useful Support Files

- `references/education-service-agent-requirements.md` — example synthesis from an education-service AI Agent requirements bundle.
