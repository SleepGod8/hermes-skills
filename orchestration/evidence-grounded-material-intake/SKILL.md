---
name: evidence-grounded-material-intake
description: "Use when turning documents into agent evidence."
version: 1.0.0
author: "Hermes Agent"
license: MIT
platforms: [windows, linux, macos]
tags: [evidence, OCR, documents, multi-agent, novel-workshop, provenance]
metadata:
  hermes:
    category: orchestration
    tags: [evidence, OCR, documents, multi-agent, novel-workshop, provenance]
---

# Evidence-Grounded Material Intake

## Purpose

Convert explicitly supplied local material into a traceable evidence packet for downstream agent workflows. This skill is a preprocessing and provenance layer. It does not freeze engineering contracts, write project constitutions, update task hard constraints, or promote extracted content to novel canon.

## Use when

- A multi-agent development task includes user-specified images, PDFs, scans, screenshots, or legacy documents.
- A novel workshop receives character sheets, old drafts, reference documents, or scanned notes.
- Downstream agents need source IDs, page references, OCR confidence, sensitive-field warnings, and separation between extracted facts and proposals.

Do not use it for ungrounded personality imitation, automatic directory crawling, unattended corpus ingestion, or autonomous canon/requirements updates.

## Non-negotiable boundaries

1. Process only files the user explicitly identifies; never scan a directory by default.
2. Prefer local extraction. Do not upload or call external OCR without separate explicit authorization stating network use, data scope, and privacy risk.
3. Preserve provenance: source ID, path, page/region, extraction engine, confidence score/label, status, and sensitive-field categories.
4. Treat OCR/extraction as evidence, not truth. Low-confidence, partial, conflicting, or inferred content stays unconfirmed.
5. Never copy phone numbers, emails, tokens, cookies, or private raw text into shared agent artifacts unless the user explicitly authorizes the exact content.
6. A responsible owner must review the evidence packet before it becomes an engineering constraint or story canon.

## Standard flow

1. Identify the target and finite inputs; record exact paths and intended downstream use.
2. Extract locally; distinguish text-layer PDF extraction from scanned-page OCR.
3. Build the evidence packet with stable IDs such as `IMG-001` or `PDF-001-P003`.
4. Classify content as `EXTRACTED`, `DERIVED`, `PROPOSAL`, `PENDING`, and only after approval `CANON` or `FROZEN-CONTRACT`.
5. Screen actual OCR confidence, unreadable regions, sensitive-field categories, and human-review needs.
6. Hand off report paths and source IDs, not unreviewed raw text as hard constraints.
7. Confirm before promotion: default/Athena reviews engineering evidence; W0 reviews novel-workshop evidence; the user resolves material conflicts.
8. Verify reports exist, JSON and Markdown describe the same records, and no profile/memory/canon/contract write occurred during intake.

## Downstream integration

### Multi-agent development

Run this layer before project-constitution authoring, preflight, or task-book finalization when documents/images are inputs. Put evidence reports under `.agents/evidence/` when authorized. Constitutions, frozen contracts, and task books may reference report paths and confirmed conclusions, but must not silently promote OCR text, low-confidence claims, or sensitive values.

### Novel workshop

Run this layer before W0's material interrogation gate. W0 compares extracted material with the current Bible, asks clarifying questions, marks conflicts unresolved, and only after user approval updates the Bible and increments its version. `EXTRACTED` and `PROPOSAL` never automatically become `CANON`; unconfirmed content is not distributed as a hard constraint to W1-W4.

## Output contract

Every intake provides:

- Source list and exact input scope.
- Per-source report with stable IDs.
- Engine, page/region, confidence score and label, status, and sensitive-field categories.
- Extracted-text location or redacted summary.
- Unreadable/failed/partial areas.
- Network and persistence statement.
- Promotion decision: `not promoted`, `pending review`, or explicitly approved target artifact.

Reuse the local `persona-distillation` skill and its `scripts/ocr_extract.py` for extraction; reuse `ocr-report-v1` when available rather than inventing a second incompatible schema.

## Failure handling

- Missing OCR engine: report `failed` honestly; never claim the document is empty.
- Text-layer PDF: use direct extraction and mark `pymupdf`; do not force OCR unnecessarily.
- Scanned PDF: render and OCR pages individually; preserve failed-page IDs.
- Low confidence or complex layout: mark `partial`/`low`, request review, and block promotion.
- Sensitive detection: report categories only by default and pause promotion until redaction/approval.
- Any write or upload ambiguity: stop and ask; intake is read-only by default.

## Completion definition

Intake is complete only when finite input scope, source IDs, reports, confidence/status fields, sensitive-field review, network/persistence status, and promotion decision are explicit. Successful OCR alone is not completion.

## Maintenance

Keep extraction implementation details in `persona-distillation`; keep this class-level skill focused on provenance, handoff, and promotion gates. If the report schema changes, update both producer and this integration contract together.

See `references/integration-checklist.md` for the reusable handoff checklist and acceptance matrix.
