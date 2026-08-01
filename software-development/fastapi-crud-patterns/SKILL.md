---
name: fastapi-crud-patterns
description: "FastAPI + SQLAlchemy + Pydantic CRUD 开发模式和常见坑"
version: 1.0.0
author: agent
license: MIT
tags: [fastapi, sqlalchemy, pydantic, crud, python]
---

# FastAPI CRUD 开发模式

FastAPI + SQLAlchemy + Pydantic 三层分离标准模式，以及学习过程中常见的坑。

## 何时使用

- 搭建 FastAPI CRUD 项目
- 用户学习 FastAPI/Pydantic/SQLAlchemy 基础
- 排查 FastAPI 项目的常见错误（循环导入、类型推断、datetime 导入等）

## 标准项目结构（三层分离）

```
项目/
├── models.py      # SQLAlchemy ORM 表定义
├── schemas.py     # Pydantic 请求/响应体
├── crud.py        # 数据库操作逻辑（增删改查）
├── database.py    # 数据库引擎 + get_db 依赖
├── routers.py     # APIRouter 路由层
└── main.py        # FastAPI 入口，注册路由
```

**关键原则：** database.py 被所有人引用，但它自己不引用任何人 —— 这是打破循环导入的核心。

## 从参考项目优化简易 FastAPI 项目

当用户要求“以某个成熟项目为参考”优化当前简易项目时，优先迁移**可低风险落地的工程层能力**，不要一次性照搬整个目录树：

1. 先对比参考项目的稳定横切层：`core/config.py`、`core/response.py`、`core/permissions.py`、文件解析服务、异常处理、路由聚合。
2. 对当前项目做小步迁移：新增轻量 `core/config.py`，让 `database.py` 从 settings 读取 `DATABASE_URL`；新增 `core/response.py`/`core/permissions.py` 作为后续标准化基础。
3. 把 `main.py` 中的文件解析、业务规则等膨胀逻辑抽到服务文件，例如 `file_parser.py`、`services.py`，保持入口文件只负责路由装配。
4. 保持旧接口响应形状不破坏已有前端和测试；统一响应体可以先作为新增接口/后续迁移的工具，不要强行全量改造。
5. 每一轮迁移后立即跑 `pytest`，再重启 uvicorn 并做 1-2 个真实 HTTP 探针确认服务可用。

## 循环导入问题（高频坑）

**症状：** Swagger 测试返回 `500 Undocumented Error: Internal Server Error`

**根因：** `routers.py` 写 `from main import get_db`，`main.py` 写 `from routers import router`，形成循环。

**修复：** 把 `get_db`、`engine`、`SessionLocal` 抽到 `database.py`：

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./employment.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

```python
# routers.py — 从 database 导入，不再从 main
from database import get_db

# main.py
from database import engine
from routers import router
```

```
❌ main → routers → main         ✅ main → database ← routers
```

## datetime 导入错误

**症状：** IDE 报 `datetime` 类型无效

**根因：** `import datetime` 导入的是模块，不是类。Pydantic 需要 `datetime.datetime` 这个类。

**修复：**
```python
# ❌ 错误
import datetime
date: datetime = Field(...)

# ✅ 正确
from datetime import datetime
date: datetime = Field(...)
```

## SQLAlchemy 类型推断误判

**症状：** IDE 报 `应为类型 'Employment'，但实际为 'type[Employment]'`

**根因：** SQLAlchemy 1.x 的 `query().first()` 返回类型对 PyRight/PyCharm 难以推断。

**方案一（推荐）：** 用 SQLAlchemy 2.0 风格
```python
from sqlalchemy import select

emp = db.execute(
    select(Employment).where(Employment.id == employment_id)
).scalar_one_or_none()
```

**方案二：** `cast()` 显式标注
```python
from typing import cast
return cast(Employment, emp)
```

## Requirements-Driven Prototype Hardening

When asked to optimize a simple FastAPI prototype against a developer requirements specification, treat traceability and closed-loop workflows as first-class deliverables. Add missing source/audit/readback tables and endpoints before cosmetic refactors: customer source records, judgment records, knowledge chunks, operation logs, notifications, complaint handling, and psychological alert follow-up. Preserve existing response shapes unless the user explicitly wants a breaking redesign. See `references/requirements-driven-fastapi-ai-platform.md` for a concrete pattern and pitfalls from an education-service AI platform.

## Dify Workflow AI Adapter

When a project has rule-based AI features and the user asks to implement them through Dify workflows, add a centralized Dify client and route every AI capability through “Dify first, local fallback” service functions. Keep credentials in env vars only, preserve backend ownership of DB writes/audit logs, and keep NL2SQL protected by backend SELECT-only validation. See `references/dify-workflow-ai-adapter.md` for the concrete pattern.

For Dify 1.16 self-hosted, prefer the official Service API shape: each Workflow App has its own `app-*` API key and `/v1/workflows/run` runs that app's default published workflow. Do not model it as one global API key plus multiple workflow IDs unless the deployment explicitly supports that. If creating workflow records programmatically, verify control-panel compatibility as well as API execution; Dify expects `kind='standard'`, serialized variable stores such as `conversation_variables`/`rag_pipeline_variables` as `{}`, and no stale `#sys.query#` references in generated nodes. See `references/dify-116-workflow-app-key.md` for the concrete pitfall checklist.

## FastAPI Frontend Template Preview

When asked to adapt/find a frontend template for a FastAPI prototype, create a non-destructive preview route first (for example `/template-preview`) using a domain-appropriate admin/dashboard template and wire it to real APIs before replacing the homepage. See `references/fastapi-frontend-template-preview.md`.

## 创建 vs 修改的 Schema 设计

| | EmploymentCreate | EmploymentUpdate |
|---|---|---|
| 用途 | 新增 | 修改 |
| 必填字段 | 多 | 无（全 Optional） |
| id | 在请求体里 | 在 URL 路径里 |

**修改关键技巧 —— exclude_unset：**
```python
def update_employment(db, employment_id, data: EmploymentUpdate):
    emp = get_employment(db, employment_id)
    update_data = data.model_dump(exclude_unset=True)  # 只取用户传了的字段
    for key, value in update_data.items():
        setattr(emp, key, value)
    db.commit()
    return emp
```

不用 `exclude_unset=True` 的话，所有 Optional 字段都会变成 `None`，把数据库里的值覆盖掉。

## DAO update() 的 None 跳过陷阱

**症状：** `dao.update(user, {"department": None, "department_path": None})` 后字段值没变。

**根因：** BaseDAO.update() 默认跳过 None 值，防止意外覆盖已有数据：
```python
if v is None and not clear:
    continue   # ← None 被静默跳过
```

**修复：** 传 `_clear=True` 标记告诉 DAO 允许置空：
```python
update_data["department"] = None
update_data["department_path"] = None
update_data["_clear"] = True
dao.update(obj, update_data)
```

`_clear` 是 DAO 内部约定 key（被 pop 掉不写入数据库）。只在主动清空字段时使用，普通更新仍走默认行为（跳过 None）。

## 筛选查询模式

在查询接口上加可选参数实现筛选，不传就不筛：

```python
def get_employments(db, skip=0, limit=100, student_id=None, company_name=None, min_salary=None, max_salary=None):
    query = db.query(Employment)
    
    if student_id:
        query = query.filter(Employment.id.like(f"%{student_id}%"))
    if company_name:
        query = query.filter(Employment.company_name.like(f"%{company_name}%"))
    if min_salary is not None:
        query = query.filter(Employment.salary >= min_salary)
    if max_salary is not None:
        query = query.filter(Employment.salary <= max_salary)
    
    return query.offset(skip).limit(limit).all()
```

## Pydantic Field 速查

| 参数 | 作用 | 示例 |
|------|------|------|
| `...` | 必填 | `Field(...)` |
| `None` | 可选 | `Field(None)` |
| `ge` / `le` | 数值范围 | `Field(ge=1, le=150)` |
| `min_length` / `max_length` | 字符串长度 | `Field(min_length=1, max_length=50)` |
| `pattern` | 正则校验 | `Field(pattern="^(男\|女)$")` |
| `default` | 默认值 | `Field(default="未就业")` |
| `description` | 文档描述 | `Field(description="姓名")` |

## Optional 含义

```python
Optional[int]  =  Union[int, None]
# 这个字段可以是 int，也可以是 None（即不传也行）
```

| 写法 | 必填 | 能传 None |
|------|:--:|:--:|
| `age: int` | ✅ | ❌ |
| `age: Optional[int]` | ❌ | ✅ |

## Column 常用参数

| 参数 | 作用 |
|------|------|
| `primary_key=True` | 主键，唯一+非空+自动索引 |
| `autoincrement=True` | 自动递增 |
| `nullable=False` | 不能为空 |
| `unique=True` | 值不能重复 |
| `default=...` | 默认值 |
| `index=True` | 建索引加速查询 |
| `onupdate=func.now()` | 每次更新自动刷新时间戳 |
