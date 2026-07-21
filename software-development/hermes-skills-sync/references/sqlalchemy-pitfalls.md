# SQLAlchemy Column Pitfalls (Chinese Developers)

## Critical: Column first argument is the DATABASE COLUMN NAME

```python
# ❌ WRONG — 数据库列名变成中文 "学生编号"
id = Column("学生编号", Integer, primary_key=True)

# ✅ RIGHT — 列名是 id，注释是中文
id = Column(Integer, primary_key=True, comment="学生编号")
```

`Column()` signature: `Column(name, type_, *args, **kwargs)`

The first positional argument is the database column name. If you pass a Chinese string, the column in MySQL will have that Chinese name. This is almost never what you want.

Use `comment=` for human-readable descriptions.

## Detection Pattern

When debugging a FastAPI + SQLAlchemy project with Chinese-speaking developers, scan all model files for this pattern:

```bash
grep -n 'Column("' app/models/*.py
```

If the first argument contains Chinese characters, it's wrong.

## Related: Model ↔ Schema Field Alignment

Always verify that Pydantic schema field names match SQLAlchemy model column names:

```python
# Check: schema fields that don't exist in model
model_cols = {c.name for c in Model.__table__.columns}
schema_fields = set(Schema.model_fields.keys())
mismatch = schema_fields - model_cols  # should be empty (or only fields model auto-generates)
```

## Related: Auto-increment vs Manual Primary Key

When the user fills in the primary key value (like `id=0001`):
- The model should **not** have `autoincrement=True`
- The schema should include `id` as a required field
- Type must match between model and schema (int vs str)

When the database generates the primary key:
- Model has `autoincrement=True`
- Schema should **not** include `id` in create requests
