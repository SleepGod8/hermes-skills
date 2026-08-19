# 模型切换 / 熔断记录

> 文件建议位置：`.agents/checkpoints/model-switch-{{TASK_ID}}-{{TIMESTAMP}}.md`

## 1. 基本信息

| 项 | 内容 |
|---|---|
| 时间 | {{TIMESTAMP}} |
| 任务 ID | {{TASK_ID}} |
| Agent | {{AGENT_NAME}} |
| 原模型/Provider | {{OLD_MODEL}} / {{OLD_PROVIDER}} |
| 新模型/Provider | {{NEW_MODEL}} / {{NEW_PROVIDER}} |
| 触发原因 | 超时 / stale / 401 / 429 / 5xx / 质量不达标 / 工具不可用 / 其他 |

## 2. 切换前状态

- 已完成动作：
  - {{DONE_ACTION_1}}
- 已修改文件：
  - {{CHANGED_FILE_1}}
- 已执行验证：
  - `{{VERIFY_CMD}}` → {{RESULT}}
- 未完成动作：
  - {{PENDING_ACTION_1}}

## 3. 副作用与安全检查

| 检查项 | 结果 | 证据/说明 |
|---|---|---|
| 是否有文件写入 | YES/NO | {{EVIDENCE}} |
| 是否有数据库/迁移操作 | YES/NO | {{EVIDENCE}} |
| 是否有外部 API/发布/消息发送 | YES/NO | {{EVIDENCE}} |
| 是否可重复执行 | YES/NO | {{EVIDENCE}} |
| 是否需要 Athena/主人确认 | YES/NO | {{EVIDENCE}} |

## 4. 恢复方案

1. 新模型先只读检查当前文件和任务状态。
2. 不重复执行已经产生外部副作用的动作。
3. 根据未完成动作继续推进。
4. 完成后由 Eos 重新验证受影响范围。

## 5. 最终结论

- 切换是否成功：YES/NO
- 剩余风险：{{RISK}}
- 下一步：{{NEXT_STEP}}
