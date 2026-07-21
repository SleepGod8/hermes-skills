# 种子数据脚本编写检查清单

## 预检（运行前）

- [ ] 所有 `status` 值匹配 Schema 的 `pattern` / `Literal`
  ```python
  import re
  p = re.compile(r"^(未就业|就业开放中|已签约|已入职|已违约)$")
  for s in status_values:
      assert p.match(s), f"非法状态: {s}"
  ```
- [ ] `student_id` 对已存在的学生，且没有重复录入（`student_id` 在 employment 表有 `unique=True`）
- [ ] Score 没有 `subject` 字段（仅 `student_id`, `exam_no`, `score`, `remark`）
- [ ] 学生 `student_no` 唯一（primary_key）
- [ ] 数据库表已创建（`init_db` 已跑过）

## Schema ↔ Model 字段一致性

| 层 | 要检查的字段 | 常见错误 |
|------|------|----------|
| Model | `Column(...)` 列名、类型 | 中文列名陷阱 |
| Create Schema | `Field(...)` 约束（pattern, ge, max_length） | 状态值不全 |
| Update Schema | 与 Create 共享的 pattern | 同上 |
| Response Schema | 继承 Create → 继承所有约束 | pattern 太严导致 500 |

## 运行时检查

- [ ] 表列名确认：`DESC tablename`
- [ ] 调用 API 测试：`POST /employment` → 200
- [ ] 调用 API 查询：`GET /employment` → 200，数据符合预期
- [ ] 调用 API 筛选：`GET /employment?student_id=xxx` → 正确过滤

## 清理

- `seed_*.py` 脚本用完即删（Git 不提交）
- 推荐一步完成：`python seed_*.py && rm seed_*.py && pytest`
  - 避免脚本残留工作区触发系统重复验证
  - 数据写完后立即删除，不阻塞后续操作
- 数据库状态应在 `pytest` 后确认没污染测试

## 文件命名约定

| 用途 | 命名 | 说明 |
|------|------|------|
| 首次填充 | `seed_data.py` | 基础演示数据 |
| 后续补充 | `seed_more.py`, `seed_extra.py`, `seed_demo2.py` | 在已有数据基础上追加，含 `existing_emp` 去重检查 |
| 一次性 | 任意 `seed_*.py` | 用后即删，勿提交 |

## 去重策略（employment 表 `student_id` 有 unique 约束）

```python
existing_emp = {e.student_id for e in db.query(Employment).all()}
emps = [e for e in new_emps if e.student_id not in existing_emp]
db.add_all(emps)
```