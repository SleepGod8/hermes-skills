---
name: codebase-review
description: "Inspect a codebase and report issues without modifying — read-only audit and problem listing."
version: 1.0.0
tags: [code-review, audit, inspection, ro]
---

# Codebase Review (Read-Only Audit)

Inspect a project codebase and list all issues found. **Do NOT modify any files** unless explicitly asked.

## When to Use

- User says "检查代码有没有问题" / "看看代码有什么问题" / "check my code"
- User says "有问题告诉我但不要修改" / "don't modify, just tell me"
- User asks for a code audit or code quality review

## Workflow

### Phase 1: Map the project
```bash
find <project> -name "*.py" -not -path "*/.venv/*" -not -path "*/__pycache__/*" | sort
```
Get a complete file list to understand structure.

### Phase 2: Read all files
Read every `.py` file. Pay special attention to:
- Imports (unused, broken, circular)
- Class/model definitions (missing primary keys, wrong column types)
- Config files (hardcoded secrets)
- Duplicate/conflicting files
- Entry points (can the app actually start?)

### Phase 3: Report findings
Organized by severity:
- 🔴 **Critical** — App won't start, data loss, security
- 🟡 **Moderate** — Wrong but won't crash, tech debt
- 🟢 **Minor** — Style, naming, conventions

Each issue: file path, line number, code snippet, explanation, fix suggestion.

## Pitfalls

- **Don't modify by default.** User explicitly said "不要修改" — respect that.
- **Check for duplicate model definitions** — common in student/team projects where members work independently.
- **Column name vs comment** — Chinese students often write `Column("中文名", ...)` instead of `Column(..., comment="中文名")`. Flag this.
- **Two entry points** — Root `main.py` vs `app/main.py` often indicates merger of two independent codebases.
- **tests/conftest.py importing wrong app** — Verify the test app matches the real entry point.
- **Pydantic V1 vs V2 syntax** — `class Config: from_attributes = True` vs `model_config = {"from_attributes": True}`.
- **Hardcoded credentials** — DB passwords in source code, even with `***` placeholder.
- **SQL reserved words as table names** — `class`, `order`, `group` etc.

## Verification

Run `pytest` with correct Python to confirm tests pass:
```bash
PYTHONPATH="" /path/to/venv/python -m pytest tests/ -v --tb=short
```
Note: conda envs on Windows may need `PYTHONPATH=""` to avoid Hermes venv pollution.

## Reference

See `references/common-issues.md` for a catalogue of recurring bugs found in student/team projects.
