# MySQL Column Conflict Debugging

When FastAPI returns `500 Internal Server Error` with `Unknown column 'table.field'` but the model clearly defines that field.

## Root Cause: Two Projects Sharing One Database

- Project A created tables with Chinese column names (`Column("学生编号", Integer)` → DB column is literally `学生编号`)
- Project B queries the same table expecting `student_no` → MySQL error

## Diagnosis Flow

### Step 1 — Identify which endpoint fails

```bash
curl http://127.0.0.1:8001/api/v1/students
# {"code": 500, "message": "服务器内部错误", "data": null}
```

### Step 2 — Check server log for the real SQL error

```bash
# uvicorn background process output
tail -f server.log | grep "Unknown column"
# → Unknown column 'students.student_no' in 'field list'
```

### Step 3 — Verify actual table columns vs model

```bash
python -c "
import pymysql
conn = pymysql.connect(host='localhost', user='root', password='xxx', database='db')
cur = conn.cursor()
cur.execute('DESC students')
for r in cur.fetchall():
    print(f'{r[0]:25s} {r[1]:15s}')
"
```

Compare output with model columns in `app/models/student.py`. If they don't match (e.g. DB has `学号` but model has `student_no`), the table was created by a different project's schema.

### Step 4 — Check which tables belong to which project

```bash
cur.execute('SHOW TABLES')
tables = [r[0] for r in cur.fetchall()]
```

Compare with `__tablename__` in each model file. Tables from a stale project won't match any current model's column list but will match the name.

## Fix

### Option A — Keep the current project's models (recommended)

Drop old tables, recreate from current models:

```python
tables = ['students', 'scores', 'employment', 'teachers', 'class', 'class_teachers']
for t in tables:
    cur.execute(f'DROP TABLE IF EXISTS `{t}`')
```

Then re-run the current project's init script:
```bash
python -m app.init_db
```

**Warning**: This destroys ALL data in those tables. Only safe on empty dev databases.

### Option B — Add migration to rename columns

Use raw SQL `ALTER TABLE` to rename Chinese columns to English names — fragile and error-prone for a project in development.

## Prevention

When starting a new team project sharing an existing MySQL database:

1. Take note of existing tables before running `init_db`:
   ```sql
   SHOW TABLES;
   ```
2. If tables with the same name exist from another project, drop them first
3. Run init_db fresh
4. Verify with `DESC` that column names match your models

## Windows Shell Warning

On Windows git-bash, avoid inline Python with f-strings containing `{t}`:

```bash
# ❌ BROKEN — bash expands {t}
python -c "for t in tables: print(f'table={t}')"

# ✅ WORKS — write to file first
echo 'tables = ["a","b"]; [print(f"table={t}") for t in tables]' > fix.py
python fix.py
```
