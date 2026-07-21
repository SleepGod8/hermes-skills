# Common Issues Found in Chinese Student Projects

These are recurring patterns found across multiple student team projects. Check for these in every review.

## Column Name vs Comment

```python
# ❌ Wrong — database column becomes Chinese
id = Column("学生编号", Integer, primary_key=True)
name = Column("姓名", String(50))

# ✅ Correct
id = Column(Integer, primary_key=True, comment="学生编号")
name = Column(String(50), comment="姓名")
```

**Why it matters:** SQLAlchemy's first positional arg is the column *name* in the database. Chinese column names cause issues with ORM queries and migrations.

## Missing Primary Key

```python
# ❌ Missing primary_key=True
class Class(Base):
    __tablename__ = "class"
    class_id = Column(String(20), unique=True, nullable=False)
    # No primary key — SQLAlchemy will error on create_all()

# ✅ Fixed
class Class(Base):
    __tablename__ = "class"
    class_id = Column(String(20), primary_key=True, comment="班级编号")
```

## Duplicate Models (Team Merge Bug)

When team members work independently and merge later, you often get:

```
app/models/employment.py  → class Employment, table "employment", fields A,B,C
app/employment.py         → class Employment, table "employment", fields X,Y,Z
```

Both inherit from `Base`, both map to same table. Creates silent data corruption or startup errors.

## Pydantic V1/V2 Mixing

```python
# V1 (old, deprecated in V3)
class Config:
    from_attributes = True

# V2 (current)
model_config = {"from_attributes": True}
```

## Undefined Variable on Import

```python
# Import commented out (was TODO)
# from app.routers import employment

# But usage left in — NameError at startup
app.include_router(employment.router, ...)
```

## SQL Reserved Words as Table Names

```python
__tablename__ = "class"   # class is a MySQL keyword → wrap in backticks or rename
__tablename__ = "classes" # better
```

## Hardcoded Credentials

```python
DATABASE_URL = "mysql+pymysql://root:123456@localhost/db"
```
Check both `config.py` and `.env` files. Real passwords in source code are a security issue.

## Column Semantic Mismatch

```python
student_id = Column("学生姓名", Integer, ...)
# Column comment says "name" but type is Integer — probably meant student_no
```
