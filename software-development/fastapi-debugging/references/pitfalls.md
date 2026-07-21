# FastAPI + SQLAlchemy 常见陷阱

## 陷阱 1：Column 中文名放错参数位置

```python
# ❌ 错误 — "学生编号" 成了数据库列名
id = Column("学生编号", Integer, primary_key=True)

# ✅ 正确
id = Column(Integer, primary_key=True, comment="学生编号")
```

Column 签名为 `Column(name, type, ...)`，第一个位置参数是列名不是注释。

## 陷阱 2：重复的 `__tablename__`

两个文件定义了同名表 → `InvalidRequestError: Table 'xxx' is already defined`。

必须删除重复的模型文件，保留一个。

## 陷阱 3：`autoincrement` 与手动主键

```python
# 自增主键 → Create Schema 不要包含 id
id = Column(Integer, primary_key=True, autoincrement=True)

# 手动主键 → 去掉 autoincrement，Schema 需要 id
id = Column(String(20), primary_key=True)
```

## 陷阱 4：字段类型必须一致

| 层级 | id 类型 |
|------|---------|
| Model Column | `Integer` / `String(20)` |
| Create Schema | `int` / `str` |
| Response Schema | `int` / `str` |

三层必须完全一致，否则要么 422 要么 500。

## 陷阱 5：SQL 关键字表名

`class`、`order`、`group` 等是 SQL 保留字，建议避免：
```python
__tablename__ = "classes"  # 而不是 "class"
```

## 陷阱 6：Pydantic V1/V2 混用

```python
# V1（旧）
class Config:
    from_attributes = True

# V2（新）
model_config = {"from_attributes": True}
```

## 陷阱 7：诊断 — 列名不对时查实际表结构

当报 `Unknown column 'xxx' in 'field list'` 时，不要只看 Model 定义——去数据库看实际列名：

```
mysql -u root -p -e "DESC tablename"
```

常见原因：旧项目用了 `Column("中文名", ...)` 导致数据库列名是中文，新 Model 用 `Column(..., comment="中文名")` 期望英文列名。两个项目共用同一个数据库时，旧表的列名格式会残留。

## 陷阱 8：Patch 更新中的 `supplied` 判断

当涉及「父对象 + 关联子表」一起更新时，需要区分「用户传了空值」和「用户没传」：

```python
values = data.model_dump(exclude_unset=True)
teacher_ids_supplied = "teacher_ids" in values
homeroom_supplied = "homeroom_teacher" in values

teacher_ids = values.pop("teacher_ids", None)
homeroom_teacher = values.pop("homeroom_teacher", None)

for field, value in values.items():
    setattr(item, field, value)

if teacher_ids_supplied or homeroom_supplied:
    desired_ids = teacher_ids if teacher_ids_supplied else current_ids
    ...
```

| 场景 | `"teacher_ids" in values` | 含义 |
|------|:---:|------|
| 用户没传老师列表 | `False` | 保持现状，不改关联表 |
| 用户传了 `[]` | `True` | 清空老师（显式清空） |
| 用户传了 `["T001"]` | `True` | 替换为 T001 |

注意：`teacher_ids_supplied` 不能省略，否则无法区分「用户想清空」和「用户没动」。

## 陷阱 9：`id` 的 autoincrement 与手动指定冲突

```python
# Model：自增 —— Schema 不应包含 id
id = Column(Integer, primary_key=True, autoincrement=True)

# Model：手动 —— Schema 需要 id
id = Column(Integer, primary_key=True)
```

`Duplicate entry '1' for key 'PRIMARY'` 的原因是第一次写入 id=1 成功，第二次又写 id=1。解决方案：明确 id 是自增还是手动输入，Schema 和 Model 保持一致。

## 陷阱 10：`.env` 文件未自动加载

```python
# app/config.py 只从 os.environ 读，但没人调用 load_dotenv()
# → .env 里的 DATABASE_URL 永远不会被加载
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "mysql+pymysql://root:***@localhost/wolin_sms"
)
```

**表现：** 健康检查（不需要数据库）正常 200，但任何需要查数据库的接口都 500。测试用 SQLite 所以能通过。

**解决方案：** 在 `config.py` 顶部加上：
```python
from dotenv import load_dotenv
load_dotenv()  # 读取 .env 文件到 os.environ
```

## 陷阱 11：MySQL 8.0+ caching_sha2_password 需要 `cryptography`

MySQL 8.0+ 默认使用 `caching_sha2_password` 认证插件，pymysql 需要 `cryptography` 包才能支持：

```
RuntimeError: 'cryptography' package is required for sha256_password or
caching_sha2_password auth methods
```

**排查：** 确认 `cryptography` 装在**运行时 Python 环境**下，而非其他 venv：

```bash
# 检查运行中进程的 sys.path
python -c "import sys; print([p for p in sys.path if 'site-packages' in p])"
```

Windows 下 lib/python 的包必须装在运行时环境自身的 site-packages 中，不能依赖其他 venv 提供的包——Hermes 的 venv 路径在 `sys.path` 中排在前面，但 uvicorn 的子进程可能不会继承这个路径顺序，导致找不到包。

## 陷阱 12：ResponseSchema 继承 CreateSchema 的正则校验导致 500

```python
class EmploymentCreate(BaseModel):
    status: str = Field(pattern="^(未就业|就业开放中|已签约|已违约)$")

# EmploymentResponse 继承 CreateSchema → 继承了 status 的 pattern
class EmploymentResponse(EmploymentCreate):
    model_config = ConfigDict(from_attributes=True)
```

**表现：** 查询就业列表时 `GET /api/v1/employment` 返回 500，错误为：
```
pydantic_core._pydantic_core.ValidationError
String should match pattern '...'
```

**原因：** 数据库里某条记录的 `status` 值是 `"已入职"`，但 `EmploymentResponse` 从 `EmploymentCreate` 继承的 `pattern` 正则里没有这个值。`model_validate()` 在反序列化 ORM → Pydantic 时校验失败。

**区分：**
| 场景 | Schema | 错误码 | 时机 |
|------|--------|:------:|------|
| 用户输入了非法 status | `Create` / `Update` | **422** | 请求校验 |
| 数据库已有非法 status | `Response` | **500** | 返回序列化 |

**修复方案 A（如果状态值合法）：**
```python
# 三个 Schema 的 pattern 都要加
status: str = Field(pattern="^(未就业|就业开放中|已签约|已入职|已违约)$")
```

**修复方案 B（如果状态值不合法）：**
```sql
UPDATE employment SET status = '未就业' WHERE status = '已入职';
```

**前端同步陷阱：** 后端 Schema 加了新状态后，前端下拉选项（`fields` 配置中的 `select` 数组）也必须同步添加。两者不一致时：新增记录会报 422，但查询列表正常。排查时先确认后端 `pattern`/`Literal` 与前端 `select` 选项列表一致。

## 陷阱 13：前端下拉选项与后端 Schema 状态值不同步

```javascript
// app.js employment fields — 少了 "已入职"
['status','就业状态','select',false,['未就业','就业开放中','已签约','已违约']]
```

```python
# backend Schema — 有 "已入职"
status: Literal['未就业','就业开放中','已签约','已入职','已违约'] = '未就业'
```

**表现：** 前端新增/编辑就业记录时，下拉框里找不到"已入职"选项，但数据库里有记录是"已入职"。

**排查：** 对比后端 `Schema.status` 的 `pattern`/`Literal` 与前端 `fields` 中的 `select` 选项数组。后端支持的值必须全部在前端选项里。

**修复：** 两端同步添加缺少的状态值：
```javascript
['status','就业状态','select',false,['未就业','就业开放中','已签约','已入职','已违约']]
```

注意：浏览器缓存可能导致即使改了代码也看不到新选项，需要 Ctrl+F5 或更新 `index.html` 的版本号。
