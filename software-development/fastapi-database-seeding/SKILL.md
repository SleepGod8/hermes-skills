---
name: fastapi-database-seeding
description: Add seed/demo data to a FastAPI + SQLAlchemy + MySQL project while preserving existing records and respecting model constraints.
tags: [fastapi, sqlalchemy, mysql, seeding, demo-data, pytest]
category: software-development
---

# FastAPI Database Seeding

Add bulk demo data to a FastAPI/SQLAlchemy project without corrupting existing records.

## Trigger

User says "add sample/demo/seed data", "补充数据", "填充演示数据".

## Workflow

### 1. Survey current state

Before writing any inserts, query the database to understand what exists:

```python
from app.database import SessionLocal
from app.models.student import Student
from app.models.employment import Employment
from app.models.score import Score

db = SessionLocal()
stu = db.query(Student).filter(Student.is_deleted.is_(False)).count()
sc  = db.query(Score).filter(Score.is_deleted.is_(False)).count()
emp = db.query(Employment).filter(Employment.is_deleted.is_(False)).count()
all_s = [s for s in db.query(Student).filter(Student.is_deleted.is_(False)).all()]
emp_s = {e.student_id for e in db.query(Employment).filter(Employment.is_deleted.is_(False)).all()}
no_emp = [s for s in all_s if s.student_no not in emp_s]
```

### 2. Identify constraints that can cause failures

| Constraint | How it breaks | Mitigation |
|-----------|---------------|------------|
| Unique PK | Duplicate `student_no`, `employment.id` | Always generate fresh IDs |
| Unique index | `employment.student_id` is unique | Check `emp_s` before inserting employment |
| FK reference | Student must exist before employment | Add employment only for existing students |
| `Literal` / `pattern` | `status` not in allowed list | Use exactly: `未就业`, `就业开放中`, `已签约`, `已入职`, `已违约` |
| NOT NULL | Missing required field | Check model columns before writing |

### 3. Build the seed script

- Write a standalone Python script (e.g. `seed_extra.py`) in the project root
- Import models from the project's ORM layer
- Set `DATABASE_URL` via `os.environ` so it uses MySQL (not test SQLite)
- Wrap in try/except with `db.rollback()` on failure
- Skip existing records: `emps = [e for e in new_emps if e.student_id not in existing_emp]`

### 4. Run and clean up

```bash
cd /path/to/project && PYTHONPATH="" python seed_extra.py
rm seed_extra.py
pytest tests/ -q --tb=line
```

### 5. Verify

- Check that existing data wasn't altered (counts increased, not reset)
- Check that `total` returned by the API matches expectations
- Run full test suite (tests use SQLite, independent of MySQL seeding)

## Pitfalls

- **Don't hardcode `id` for auto-increment PKs** — let the DB generate them
- **Employment is 1-per-student** — `employment.student_id` has `unique=True`. You cannot add a second employment record for the same student
- **The user wants some students without employment** — deliberately leave a few students out of the employment inserts
- **Delete the seed script after running** — stray `seed_*.py` files confuse the workspace tracker
- **`.isoformat()` on dates** — when constructing datetime values, use `datetime(2026, 1, 15)` not strings
- **`db.query(...)` in the same transaction as inserts** — wrap the survey query in a separate `SessionLocal()` or run it before the try block to avoid mixing
- **Multi-round seeding needs range planning** — after any seeding round, the next one must use a fresh `student_no` range. Query `db.query(func.max(Student.student_no)).scalar()` before each round to find where the last round stopped, then start the new IDs from there. Without this, new student IDs collide with existing ones.
- **Employment status values must match frontend dropdown too** — the backend schema enforces status via `Literal`, but the frontend module config (`app.js`) has its own array for the `status` select field. If you seed records with a status the frontend doesn't list, users can't edit that field. Always check BOTH locations when adding or renaming status values.
