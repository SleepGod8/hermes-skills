"""Seed template for FastAPI + SQLAlchemy + MySQL projects.

Copy this file to your project root, edit the data arrays, then:
    cd /path/to/project && PYTHONPATH="" python this_file.py
"""
import os, sys
sys.path.insert(0, '.')
os.environ['DATABASE_URL'] = 'mysql+pymysql://root:password@127.0.0.1:3306/dbname?charset=utf8mb4'

from datetime import datetime, date
from app.database import SessionLocal
from app.models.student import Student
from app.models.score import Score
from app.models.employment import Employment

db = SessionLocal()
try:
    # ── Survey existing data ──
    existing_emp = {e.student_id for e in db.query(Employment).all()}
    existing_stu = {s.student_no for s in db.query(Student).all()}

    # ── Insert new records ──
    # Example: students
    students = [
        # Student(student_no="...", class_id="...", name="...", ...),
    ]
    db.add_all(students)

    # Example: scores (no subject field — use exam_no)
    scores = [
        # Score(student_id="...", exam_no="...", score=..., remark="..."),
    ]
    db.add_all(scores)

    # Example: employment (skip existing — student_id is unique)
    new_emps = [
        # Employment(student_id="...", student_name="...", class_id="...", ...),
    ]
    emps = [e for e in new_emps if e.student_id not in existing_emp]
    db.add_all(emps)

    db.commit()

    # ── Report ──
    n_stu = db.query(Student).count()
    n_sc  = db.query(Score).count()
    n_emp = db.query(Employment).count()
    all_s = db.query(Student).all()
    emp_s = {e.student_id for e in db.query(Employment).all()}
    no_emp = [s for s in all_s if s.student_no not in emp_s]
    added = len(students) + len(scores) + len(emps)
    print(f"✅ Added {added}: students {n_stu} | scores {n_sc} | employment {n_emp}")
    print(f"   Students w/o employment ({len(no_emp)}): {[s.student_no for s in no_emp]}")

except Exception as e:
    db.rollback()
    print(f"❌ {e}")
finally:
    db.close()
