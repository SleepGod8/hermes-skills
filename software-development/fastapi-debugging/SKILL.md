---
name: fastapi-debugging
description: "FastAPI + SQLAlchemy 常见 bug 模式与调试流程"
version: 1.0.0
tags: [fastapi, sqlalchemy, debugging, pydantic, mysql]
---

# FastAPI + SQLAlchemy 调试手册

Column 中文名陷阱、Schema-Model 字段不一致、表结构冲突等高频问题的诊断与修复。

## 触发条件

- FastAPI 项目返回 500 Internal Server Error
- `TypeError: 'xxx' is an invalid keyword argument for Model`
- `ResponseValidationError` 类型不匹配
- SQLAlchemy `Table already defined` 冲突
- `IntegrityError: Duplicate entry` 主键冲突

## 调试流程

### 1. 看错误类型定位

| HTTP | 错误 | 含义 |
|------|------|------|
| 500 | `TypeError: invalid keyword argument` | Schema 字段和 Model 列名不一致 |
| 500 | `ResponseValidationError` | Response Schema 类型和 Model 不匹配 |
| 500 | `Table doesn't exist` | 表未建 |
| 500 | `already defined` | 两个 Model 用了同一个 `__tablename__` |
| 500 | `Duplicate entry` | 主键冲突 |
| 500 | `ValidationError: pattern_mismatch` | ResponseSchema 继承 CreateSchema 的正则，数据库数据不匹配 | 见 trap 12 |

### 2. 验证 Schema ↔ Model 一致性

```python
model_cols = {c.name for c in Model.__table__.columns}
schema_fields = set(Schema.model_fields.keys())
print(model_cols - schema_fields)  # Model 有但 Schema 没有
print(schema_fields - model_cols)  # Schema 有但 Model 没有
```

### 3. 表重建

修改 Model 后 DROP + create_all：
```sql
DROP TABLE IF EXISTS tablename;
```
```python
Base.metadata.create_all(bind=engine)
```

验证列名：`DESC tablename`

## 常见陷阱

详见 `references/pitfalls.md`
详见 `references/frontend-caching.md` — 修改 `app/static/` 下的 JS/CSS 后浏览器不刷新
详见 `references/pydantic-response-validation.md` — ResponseSchema 继承 CreateSchema 的 pattern 导致 500
详见 `references/windows-troubleshooting.md` — Windows 端口冲突、uvicorn reloader 子进程环境隔离、Hermes venv 路径冲突
详见 `references/seed-data-checklist.md` — 种子数据脚本编写检查清单
详见 `references/pydantic-three-layer.md` — Create/Update/Response 三层 Schema 模式详解

| # | 陷阱 | 症状 | 排查 |
|---|------|------|------|
| 10 | `.env` 未加载 | 健康检查 200，业务接口 500 | `config.py` 缺 `load_dotenv()` |
| 11 | `cryptography` 缺失 | MySQL 连接 `RuntimeError: caching_sha2_password auth` | 确认包装在运行时 python 环境 |
| 12 | ResponseSchema 正则继承 | 列表查询返回 500 `pattern_mismatch` | 数据库值不在 pattern 内；区分 422（请求）vs 500（响应） |
| 13 | Ghost PID (TIME_WAIT) | 端口被占但 taskkill 找不到进程 | 见 `references/windows-troubleshooting.md` → Ghost PID |
| 15 | 前端筛选项字段名 ≠ 后端参数名 | 前端筛选输入无响应（无报错） | 前端 `filters[{field:\"X\"}]` → URL `?X=val` → 后端必须有同名 `X` 参数 |
| 16 | Seed 数据 status 不合 pattern | 创建时报 422 或查询时 500 | 创建前用 `re.match(pattern, val)` 预检所有状态值 |
| 17 | 前端下拉选项与后端 Schema 状态值不同步 | 前端下拉缺选项但后端支持 | 对比后端 `pattern`/`Literal` 与前端 `fields` `select` 数组 |

## 辅助工具：ORM 转 JSON（serialize）

接口返回 ORM 对象前必须转成 JSON 兼容字典：

```python
def serialize(item):
    return XxxResponse.model_validate(item).model_dump(mode="json")
```

两步走：
1. `model_validate(item)` — `from_attributes=True` 读 ORM 属性
2. `.model_dump(mode="json")` — datetime 等类型自动转字符串

## 三层 Schema 架构速查

| Schema | 何时使用 | 关键配置 |
|--------|----------|----------|
| `Create` | POST 请求体 | 必填校验 + `@model_validator` |
| `Update` | PUT 请求体 | 全部可选 + 配合 `exclude_unset=True` |
| `Response` | 返回序列化 | `from_attributes=True` + 注意继承的约束 |

## Windows 环境调试

### 端口冲突

| WinError | 含义 |
|----------|------|
| 10013 | 端口被占用 |
| 10048 | 地址已在使用 |

```bash
netstat -ano | grep 8000 | grep LISTENING
taskkill -F -PID <pid>
```

注意：`uvicorn --reload` 创建的子进程被 `taskkill -F` 杀掉后，旧连接进入 TIME_WAIT 状态持续约 2 分钟。换端口可跳过等待。

### Hermes venv 覆盖项目环境

当 `sys.path` 中 Hermes venv 排在 conda venv 前面时：
- 包可能装到 Hermes venv 而非项目环境
- 同一包不同版本导致奇怪错误
- 子进程可能丢失 Hermes venv 路径

排查：`python -c "import sys; [print(p) for p in sys.path if 'site-packages' in p]"`
