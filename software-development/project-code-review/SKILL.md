---
name: project-code-review
description: "Systematic code quality review of Python/FastAPI projects — read all files, categorize issues by severity, report without modifying."
version: 1.0.0
tags: [code-review, python, fastapi, inspection, quality]
---

# Project Code Review

Systematic code quality review of Python projects. Read all source files, identify issues across the codebase, categorize by severity, and report findings clearly — without modifying any code unless explicitly asked.

## When to Use

- User asks "检查一下代码有没有问题"
- User wants a project-wide code quality audit
- User adds qualifiers like "告诉我但不要修改" (report only)

## Method

### 1. Discover all Python files
```bash
find <project> -name "*.py" -not -path "*/.venv/*" -not -path "*/__pycache__/*" -not -path "*/.idea/*" | sort
```

### 2. Read ALL files systematically
Read every .py file in batches. Don't skip files or assume based on names. Use parallel read_file calls for speed.

### 3. Categorize findings by severity

| Level | Icon | Criteria |
|-------|------|----------|
| 🔴 严重 | Red circle | Won't run (NameError, ImportError), data loss risk, security hole |
| 🟡 中等 | Yellow circle | Logic bugs, type mismatches, deprecated APIs, confusing naming |
| 🟢 轻微 | Green circle | Style issues, dead code, missing comments, naming suggestions |

### 4. Report format
```
## 🔴 严重问题 (N items)
### 1. `file.py:line` — 问题简述
(code snippet showing the issue)
→ 说明原因和影响

## 🟡 中等问题 (N items)
...

## 🟢 轻微问题 (N items)
...

## 📊 总结
| 等级 | 数量 |
|------|------|
...
```

### 5. Common FastAPI/SQLAlchemy issues to check

- **Column names**: `Column("中文", ...)` puts Chinese in the DB column name. Use `Column(..., comment="中文")` instead.
- **Missing `primary_key=True`** — `class_id = Column(String(20), unique=True)` with no `primary_key=True` will fail to create the table.
- **Column type omitted** — `Column("教师编号", primary_key=True, autoincrement=True)` has no type → SQLAlchemy uses `NullType` → MySQL DDL fails. Add `Integer`.
- **Duplicate models** — Two model files with the same `__tablename__` but different columns. One is usually stale. Find which one the services import and delete the other.
- **Undefined variables** — `from app.routers import employment` commented out, but `app.include_router(employment.router)` is not → `NameError`.
- **Type mismatches** — Column typed `Integer` but Pydantic schema field typed `str` (or vice versa). Check `id` fields especially.
- **Pydantic V1 (`class Config`) vs V2 (`model_config`)** syntax — both produce warnings; V2 only removes the warning.
- **Response schema types** — `id: str` in `EmploymentResponse` but model returns `Integer` auto-increment → `ResponseValidationError`. Match the type to what the model actually returns.
- **`model_dump()` vs `__dict__`** — `r.__dict__` on ORM objects includes `_sa_instance_state` (SQLAlchemy internal). Use `Schema.model_validate(r).model_dump()` instead.
- **`class Config: from_attributes = True`** — Pydantic V1 syntax; V2 uses `model_config = ConfigDict(from_attributes=True)`.
- **Database password hardcoded** in source files instead of in `.env`.
- **Table names that are SQL reserved words** (`class`, `order`, `group`) → syntax issues.
- **Unused imports** — `from sqlalchemy import column` when no `column` is used.
- **Missing `.env` file** — project reads from environment but has no `.env` to load.
- **`load_dotenv()` never called** — `.env` file exists but `config.py` reads `os.environ.get(...)` without ever calling `load_dotenv()`. Add `from dotenv import load_dotenv; load_dotenv()` at the top of `config.py`.
- **Database password placeholder leaked** — default in `config.py` is `mysql+pymysql://root:***@localhost/db` with literal `***` as password. Replace with actual password or ensure `.env` overrides it.
- **MySQL 8.0 `caching_sha2_password` needs `cryptography`** — `RuntimeError: 'cryptography' package is required` means pymysql can't authenticate. Install `cryptography` in the runtime Python environment that the ASGI server actually runs under (not just where pip put it).

### 5b. Schema-Model alignment checks (cross-reference)

For each endpoint handler, verify the data flow matches:

```
Schema Create fields → Service model_dump() → ORM Model columns
```

Common mismatches:
- Schema has `class_id`, Model has `class_no` → TypeError on insert
- Schema fields don't match ORM columns → silent errors or 500s
- Schema has fields the model doesn't have (e.g. `subject` in Score schema but no `subject` column) → TypeError

## User Preferences

- **Report only, don't modify** — unless the user explicitly asks "帮我改"
- Use Chinese in reports for Chinese-speaking users
- Be concise, focus on what matters most first
