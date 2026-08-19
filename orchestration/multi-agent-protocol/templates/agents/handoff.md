# Agent Handoff

## 交接元数据

- 时间：`<ISO-8601>`
- 来源 Agent：`<FROM>`
- 接收 Agent：`<TO>`
- 关联任务：`<TASK_ID>`
- 工程宪法版本：`<VERSION>`
- 当前状态：`<STATUS>`

## 已完成

- <完成项及文件>

## 未完成 / 阻塞

- <剩余工作、原因、所需输入>

## 修改范围

- `<PATH>`：<变更摘要>

## 验证证据

- `<V-ID / command / report path>`

## 下一步（按顺序）

1. <可直接执行的动作>

## 风险与注意事项

- <风险、回滚点、禁止触碰区域>

## 文件锁处理

- [ ] 已在 `module-ownership.yaml` 释放或转移写锁
- [ ] 已在 `task-board.yaml` 更新任务状态
