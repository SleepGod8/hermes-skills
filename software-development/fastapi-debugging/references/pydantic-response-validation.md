# Pydantic Response Validation Error (500)

## Symptom

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for XxxResponse
field_name
  String should match pattern '...' [type=string_pattern_mismatch, input_value='实际值', input_type=str]
```

## Root Cause

**Response Schema 继承 Create Schema 的校验规则**，但数据库里存了不符合规则的数据。

```python
class EmploymentCreate(BaseModel):
    status: str = Field("未就业", pattern="^(未就业|就业开放中|已签约)$")

class EmploymentResponse(EmploymentCreate):  # ← 继承了 status 的 pattern
    id: int
    ...
    model_config = ConfigDict(from_attributes=True)
```

当数据库里有 `status='已入职'` 时，`model_validate()` 会抛出 `ValidationError`，最终返回 **500**。

## 诊断

```python
# 查数据库里有哪些不符合 schema pattern 的值
from app.database import SessionLocal
from app.models.employment import Employment
import re
pattern = re.compile(r"^(未就业|就业开放中|已签约)$")  # 从 schema 复制
db = SessionLocal()
bad = db.query(Employment).filter(~Employment.status.op("REGEXP")(pattern.pattern)).all()
print([(e.student_id, e.status) for e in bad])
```

## 修复

### 方案 A — 扩展 pattern（推荐）
在 Create + Update 两个 Schema 中都加上缺失的值：
```python
status: str = Field("未就业", pattern="^(未就业|就业开放中|已签约|已入职|已违约)$")
```

### 方案 B — 让 ResponseSchema 不继承 CreateSchema
拆开继承链，各自定义 pattern：
```python
class EmploymentCreate(BaseModel):
    status: str = Field("未就业", pattern="...")

class EmploymentResponse(BaseModel):  # 不继承 Create
    status: str  # 无 pattern，完全开放
```

### 方案 C — 改数据库数据
把不匹配的记录改成 pattern 允许的值。

## 预防

创建 Seed 数据前，先用 Schema 的 pattern 验证所有数据值：
```python
import re
p = re.compile(r"^(未就业|就业开放中|已签约|已入职|已违约)$")
for status_value in seed_data:
    assert p.match(status_value), f"非法状态: {status_value}"
```

## 相关模式

- **Scalar field constraint + from_attributes + child inheritance** = 三层联动
  - `EmploymentResponse(EmploymentCreate)` → 继承了所有 Field 约束
  - `model_config = ConfigDict(from_attributes=True)` → 允许从 ORM 取值
  - `model_validate(orm_obj)` → 触发全部继承来的 validator
  - 三者缺一都不会触发这个 bug，但组合起来就是 500
- 类似的坑：`max_length`、`min_length`、`ge`、`le`、`email` 等约束都会通过继承传递给 Response
