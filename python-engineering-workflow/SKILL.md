---
name: python-engineering-workflow
description: Use when delivering Python tasks. Correctness first.
version: 1.0.1
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [python, engineering, workflow, best-practices]
    related_skills: [fastapi-crud-patterns, systematic-debugging, test-driven-development]
---

# Python 工程交付工作流

## Overview

资深 Python 软件工程师的任务交付标准。核心原则：正确性优先于速度，最小且完整的修改，真实执行的测试验证。

## 核心原则

1. **正确性优先**：不猜测，先阅读完整上下文
2. **最小修改**：只改必需内容，不重构/格式化/升级依赖
3. **真实验证**：未实际执行时不声称"已修复"
4. **失败处理**：读取错误→分析→修复，最多10轮
5. **安全边界**：不泄露密钥，不执行危险操作

## 工作流程（七步）

### 1. 理解任务
- 确认目标和验收条件
- 区分明确要求/合理假设/未知信息
- 只在缺失信息会实质改变方案时才询问

### 2. 调查项目
- 检查项目结构、README、pyproject.toml、requirements
- 搜索相关函数、类、调用位置、数据结构、已有测试
- 确认问题根因及影响范围
- 错误修复：优先复现

### 3. 制定方案
- 简短、可执行的修改计划
- 说明修改模块及验证方式
- 避免不必要抽象

### 4. 实施修改
- 小范围、可审查的补丁
- 保持接口兼容
- 正确处理空值、边界、异常、资源释放
- 优先标准库或项目现有依赖

### 5. 编写测试
- 错误修复：增加回归测试复现原问题
- 新功能：覆盖正常路径、关键边界、失败路径
- 验证行为，不只验证实现细节
- 不删除/跳过/弱化测试

### 6. 执行验证
```bash
pytest -v <相关测试>
ruff check
ruff format --check
mypy/pyright（如有配置）
```
失败时：阅读错误→判断类型→修复→重跑，最多10轮

### 7. 检查结果
- 查看最终 diff
- 检查调试输出、临时文件、硬编码路径、秘密信息
- 确认满足验收条件
- 确认未通过修改测试掩盖问题

## 输出格式

```
结果：
一句话说明完成了什么。

主要修改：
- 文件A：行为变化说明
- 文件B：行为变化说明

验证：
- pytest test_xxx.py -v → 8 passed in 0.04s ✅
- ruff check → all checks passed ✅
（未执行需标注原因）

注意事项：
- 风险/兼容性影响/需用户决定的问题
（无则写"无"）
```

## 踩坑记录

### `agent.personality` 不是合法配置键

- `hermes config set agent.personality <name>` **不会生效**
- 正确做法：写 `SOUL.md`（全局默认）+ `agent.personalities.<name>`（可切换）
- 详见 `references/config-pitfalls.md`

## 沟通要求

- 简短、有信息量的进度更新
- 不输出冗长思维过程
- 阻塞时说明原因、已检查内容、需用户提供的信息
- 不把工作环境问题误报为代码问题
