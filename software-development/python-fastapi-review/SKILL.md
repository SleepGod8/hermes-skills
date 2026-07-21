---
name: python-fastapi-review
description: "Review FastAPI + SQLAlchemy projects for structural issues — model/schema mismatches, Column anti-patterns, missing primary keys, duplicate tables, and type errors."
version: 1.0.0
author: Hermes Agent (learned from session)
tags: [python, fastapi, sqlalchemy, code-review, pydantic, models]
---

# Python FastAPI + SQLAlchemy Project Review

Systematic review of FastAPI projects with SQLAlchemy ORM. Focuses on structural and architectural issues that cause runtime 500s, schema/model mismatches, and common student/team mistakes. Distinct from `requesting-code-review` which focuses on pre-commit security and diff review.

## When to Use

- User asks "review this project for problems" without specifying scope
- New team project handoff review
- Investigating why a FastAPI endpoint returns 500
- Finding root causes before fixing (user says "tell me what's wrong but don't change anything")

## Review Sequence

### 1. Map the project structure

```bash
find . -name "*.py" -not -path "*/.venv/*" -not -path "*/__pycache__/*" | sort
```

Identify: entry points, models, schemas, routers, services, config files.

### 2. Check for multiple entry points / parallel code bases

Look for multiple `main.py` or `app = FastAPI()` — indicates stale/unused code coexisting with active code.

### 3. Review every model file

For each `class X(Base):` check:
- [ ] Every `Column()` has proper type as first positional arg (not Chinese string)
- [ ] Every table has at least one `primary_key=True`
- [ ] No duplicate `__tablename__` across files
- [ ] Auto-increment columns match their usage

### 5. Check config.py for dotenv loading

If the project uses `.env` files (common pattern), verify `load_dotenv()` is called at module level:

```python
# app/config.py — should have this at the top:
from dotenv import load_dotenv
load_dotenv()
```

**Missing `load_dotenv()` symptom**: health check returns 200 (no DB needed), but every business endpoint returns 500 (DB connection fails). The test suite passes because tests use SQLite with inline connection strings. This is a silent deploy-killer — easy to miss.

Check the actual config.py import chain: does `database.py` → `import config` trigger `load_dotenv()` from within `config.py`? If not, the `.env` file is never read.

### 6. Cross-reference schemas against models

For each Pydantic schema, verify:
- [ ] Field names exist in the corresponding model
- [ ] Field types match model column types
- [ ] Auto-increment columns are NOT in `*Create` schemas
- [ ] `from_attributes = True` (or `model_config` equivalent) on response schemas

### 7. Review ResponseSchema for inherited constraints

### 7. Review ResponseSchema for inherited constraints

Response schemas that inherit from Create schemas **inherit all field validators** (patterns, min/max length, ge/le, etc.):

```python
class EmploymentCreate(BaseModel):
    status: str = Field(..., pattern="^(未就业|已签约)$")

class EmploymentResponse(EmploymentCreate):  # ← status 的 pattern 也继承了！
    id: int
```

If the database has `status='已入职'` (not in the pattern), `model_validate()` throws `ValidationError` → **500**.

**Fix**: Either broaden the pattern on Create to cover all valid DB values, or don't inherit — define Response separately without the constraint.

### 8. Pre-validate seed data against schema constraints

Before inserting seed data, verify every value matches the schema's regex:
```python
import re
p = re.compile(r"^(未就业|就业开放中|已签约|已入职|已违约)$")
for record in seed_employments:
    assert p.match(record.status), f"非法: {record.status}"
```

- [ ] Router imports match service function signatures
- [ ] Service imports the correct model file (not a duplicate)
- [ ] Error handling: caught vs uncaught exceptions

### 6. Run what you can

```bash
# Import test (finds syntax/dependency issues fast)
python -c "from app.main import app"

# If there's a test suite
pytest -v --tb=short
```

## Common Anti-Patterns

See `references/fastapi-sqlalchemy-pitfalls.md` for detailed examples with code.

Quick list:
1. `Column("中文", Type)` instead of `Column(Type, comment="中文")`
2. Missing `primary_key=True`
3. Auto-increment `id` in create schema
4. Schema field type ≠ model column type
5. Duplicate `__tablename__` from stale model files
7. `Column(primary_key=True)` with no type → NullType error
8. Multiple FastAPI app instances from different main files
9. **Column semantic mismatch**: column comment says one thing but type says another (e.g. `Column("学生姓名", Integer)` — comment is "姓名" but type is int)
10. **Reserved word table name**: `__tablename__ = "class"` — `class` is a MySQL reserved keyword. Prefer `classes` or `school_class`.
11. **Bug cascade pattern in team projects**: fixing one model bug exposes the next. Sequence often runs: duplicate table → missing PK → NullType → field name mismatch → response type mismatch → duplicate key. Fix + rebuild table iteratively.

### The Fix Cascade (wolin-student-system real example)

This sequence appeared in a real project with 6 model files sharing a MySQL database across two code bases:

1. Duplicate model → two `Employment` models with different field names (Fix: delete one)
2. Missing PK → `Class.class_id` had `unique=True` but no `primary_key=True`
3. NullType → `teacher_id` had `Column(primary_key=True)` without a type argument
4. Column name in wrong arg → every `Column("中文", Type)` creates Chinese-named columns
5. Response schema type mismatch → model returns `int` but schema declares `str`
6. Duplicate key on retry → old data with wrong schema still in table after model fix
7. Field name mismatch → `schema.class_id` ≠ `model.class_no` — names must align

Each `DROP TABLE` + recreate cycle reveals the next bug. Plan for it iteratively.

### Table rebuild workflow

When models change substantially, `Base.metadata.create_all()` won't alter existing tables:

```python
for t in ['table1', 'table2']:
    conn.execute(f'DROP TABLE IF EXISTS `{t}`')
Base.metadata.create_all(bind=engine)
```

Always re-run the init script and verify column names via `DESC table` after rebuild.

### Shared-Database Collision (Real Example)

When two projects share the same MySQL database, one project's bad models can poison tables for the other:

```sql
-- Project A (with Chinese-named columns) created this:
+----------+--------------+
| 学号     | varchar(20)  |   ← Chinese column names
| 姓名     | varchar(50)  |
+----------+--------------+

-- Project B (with proper English models) queries this:
SELECT students.student_no ...  -- ❌ Unknown column 'students.student_no'
```

**Diagnosis**: `DESC table_name` on the actual MySQL table shows column names are Chinese.
**Root cause**: Project A used `Column("学号", String(20))` (Chinese as name arg). Project B's models use `student_no = Column(String(20))`.
**Fix**: `DROP TABLE` and recreate from Project B's models. `Base.metadata.create_all()` won't fix an existing table — it only creates missing ones.

Always verify actual column names with `DESC` in MySQL, never assume they match the model.

### The bash-{t} Windows Pitfall

On Windows git-bash, inline Python with f-strings containing `{t}` breaks:

```bash
# ❌ bash interprets {t} as empty string
python -c "for t in tables: conn.execute(f'DROP TABLE `{t}`')"
# → MySQL syntax error near ''

# ✅ Write to a .py file and run that
echo 'import pymysql; conn=pymysql.connect(...); cur=conn.cursor(); tables=[...]; [cur.execute(f"DROP TABLE IF EXISTS `{t}`") for t in tables]' > fix.py
python fix.py
```

## Pitfalls

- **"Don't modify" mode**: Respect when user asks for review-only. Flag issues, don't fix them.
- **Hidden imports**: `from app.database import Base` vs `from common.database import Base` — two different Base classes if both exist.
- **SQLite vs MySQL**: Tests may use SQLite and pass while MySQL fails. Always verify with the actual database.
- **.env protected**: Can't read `.env` with read_file — use terminal `cat` or `grep` to inspect credentials.
- **bash eats `{t}` in Python -c scripts on Windows**: On Windows git-bash, `python -c "f'DROP TABLE `{t}`'"` — bash expands `{t}` to empty string before Python sees it, producing a cryptic `syntax near ''` error. Fix: write Python to a `.py` file and run that instead of inline -c through bash.
