# Pydantic 三层 Schema 模式：Create / Update / Response

## 模式概述

FastAPI 中每个业务模块通常定义三个 Pydantic Schema，分工明确：

| Schema | 用途 | 校验规则 | 字段特点 |
|--------|------|----------|----------|
| `XxxCreate` | 创建时用户输入 | 必填+格式校验 | 不含 `id`、时间戳等服务端生成字段 |
| `XxxUpdate` | 修改时用户输入 | 全部可选 | 不含业务主键（通常不可改） |
| `XxxResponse` | 返回给前端的数据 | 无/宽松约束 | 包含所有数据库字段 + `from_attributes=True` |

## 典型实现

```python
class EmploymentCreate(BaseModel):
    student_id: str = Field(..., min_length=1, description="学生编号")
    salary: Optional[float] = Field(None, ge=0)          # ≥0
    status: Literal['未就业','已签约'] = '未就业'          # 限定取值

    @model_validator(mode="after")
    def validate_dates(self):
        if self.offer_date and self.employment_open_date and self.offer_date < self.employment_open_date:
            raise ValueError("offer 不能早于开放时间")
        return self


class EmploymentUpdate(BaseModel):
    salary: Optional[float] = Field(None, ge=0)
    status: Optional[Literal['未就业','已签约']] = None     # 全部可选

    # 注意：没有 @model_validator，因为编辑时可能没传日期


class EmploymentResponse(EmploymentCreate):               # ← 继承 Create 的约束
    id: int
    student_name: Optional[str] = None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)        # ← 允许 ORM 对象直接构造
```

## 关键漏洞：Response 继承 Create 的约束

`EmploymentResponse(EmploymentCreate)` 会**继承** `EmploymentCreate` 里的全部 `Field(...)` 约束，包括 `pattern`、`ge`、`max_length` 等。

**问题场景：** 数据库里某条记录的 `status` 是 `"已入职"`，但 `EmploymentCreate` 的 `pattern` 只允许 `"未就业|已签约"`。`model_validate(orm_obj)` 会抛出 `ValidationError`，返回 **500**。

**解决方案：** 见 `references/pydantic-response-validation.md`。

## `from_attributes=True` 说明

```python
model_config = ConfigDict(from_attributes=True)
```

**作用：** 允许 `XxxResponse.model_validate(orm_obj)` 直接从 ORM 对象的 `.属性` 读取数据，无需先转字典。

**底层：** Pydantic 内部调用 `getattr(orm_obj, field_name)` 获取每个字段的值。

**没有它：**
```python
# ❌ 报错 —— Pydantic 不认识 ORM 对象
EmploymentResponse.model_validate(db_employee)
# → TypeError: 不知道如何处理 Employee 对象

# ✅ 必须手动转字典
data = {"id": db_employee.id, "student_name": db_employee.student_name, ...}
EmploymentResponse.model_validate(data)
```

**记忆法：** `from_attributes=True` = 「允许从对象的属性（attribute）读取数据」。

## `serialize` 辅助函数

```python
def serialize(item):
    return XxxResponse.model_validate(item).model_dump(mode="json")
```

两步：
1. `model_validate(item)` — ORM 对象 → Pydantic Schema（`from_attributes` 读属性）
2. `.model_dump(mode="json")` — Pydantic → JSON 兼容字典（datetime 转字符串）

## `exclude_unset=True` 在 Update 中的使用

```python
values = data.model_dump(exclude_unset=True)   # 只取用户传了的字段

for field, value in values.items():
    setattr(item, field, value)                 # 逐个覆盖，没传的不动
```

没有 `exclude_unset=True` 时，`model_dump()` 会把所有未传字段设为 `None`，覆盖掉数据库已有的值。

## 常见陷阱总结

| 问题 | 表现 | 原因 |
|------|------|------|
| Response 继承 Create 的 pattern | 列表查询 500 | 数据库数据不匹配 Schema 约束 |
| `from_attributes` 缺失 | `model_validate()` 报错 | 忘记加 ConfigDict |
| `exclude_unset` 缺失 | 编辑后字段被清空 | 未传字段被设为 None 覆盖 |
| 类型不一致（Model int ↔ Schema str） | 422 或 500 | 三层类型必须一致 |
