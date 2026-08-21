# OpenViking 只读工具接入 DSH EAC：工具已注册但模型不可见

场景：给 DeepSeek Harness EAC / DSH Desktop 接入 OpenViking，本地 OpenViking 服务已跑通，官方 `@openviking/dsh-memory-plugin` 的 recall/context injection 生效，但模型会话里看不到 `mcp__openviking__*` 或自建 wrapper 工具。

## 关键结论

DSH 工具可见性不是“插件注册成功 = 模型可见”。工具目录还可能被当前 agent preset 在 `system-prompt/assemble` 阶段裁剪。

在本机 `anchored-standard` preset 中，`tool-bootstrap.mjs` 会把最终组装给模型的工具集裁剪为：

- bootstrap 阶段：`bash`, `str_replace_editor`
- promoted 阶段：`bash`, `str_replace_editor`, `dev_tool_search`, `skill_search`, `skill_load`, 以及通过 `dev_tool_search` durable event 解锁的工具

因此 host/global `ctx.tools.register(...)` 成功、甚至日志显示 registered，也仍可能被最终 prompt assembly 过滤掉。

## 诊断流程

1. 确认真实 EAC profile，不要只改测试 profile：
   - 进程命令行通常指向 `--profile web-desktop`
   - profile 路径：`C:/Users/<user>/.dsh/profiles/web-desktop`
2. 确认插件确实加载：查 `logs/dsh-web.log` 中 wrapper 自己的 registered 日志。
3. 确认后端能直接调用：直接 import 已安装 wrapper，模拟 registry，调用 OpenViking MCP `grep`/`find`。
4. 如果模型仍列不出工具，检查 agent preset：
   - `C:/Users/<user>/.dsh/.agent-presets/<preset>/agent.cordis.yml`
   - `tool-bootstrap.mjs` / `router-bootstrap.mjs`
   - 搜索 `system-prompt/assemble`、`assembled.tools.filter`、`keepTools`
5. 若当前 preset 是 `anchored-standard`，优先判断是否被 `tool-bootstrap.mjs` 的 keep-set 裁剪。

## 最小只读 wrapper 设计

目标只暴露三个无破坏性工具：

- `openviking_find`
- `openviking_grep`
- `openviking_read`

原则：

- 只走 OpenViking 本地 HTTP/MCP `/mcp`。
- 不暴露 `remember`、`write`、`edit`、`forget`、`add_resource` 等写入/删除能力。
- `viking://...` URI 不要交给 bash/filesystem 工具。
- 输出设上限（如 12000 chars），请求设 timeout（如 15000ms）。
- API key 配在 profile `cordis.patch.yml`，日志和汇报必须脱敏。

## 注册注意点

普通插件内注册：

```js
ctx.tools.register(defineTool({...}))
```

如果要尝试 agent scoped 工具，可监听：

```js
export const inject = ['tools', 'agents']

ctx.on('agent/session-start', ({ agent }) => {
  agent.ctx.tools.register(definition)
})
```

但注意：agent-scoped 注册仍可能被 preset 的 prompt assembly 过滤。最终是否给模型，要看 `system-prompt/assemble` 后的 `assembled.tools`。

## anchored-standard 允许 OpenViking 工具常驻的补丁形态

在 `anchored-standard/tool-bootstrap.mjs` 中加入常驻本地工具：

```js
const RESIDENT_LOCAL_TOOLS = ['openviking_find', 'openviking_grep', 'openviking_read']
```

promoted 阶段 keep-set：

```js
const keep = new Set([
  ...bootstrapTools,
  ...RESIDENT_DISCOVERY_TOOLS,
  ...RESIDENT_LOCAL_TOOLS,
  ...unlockedFor(context.agent?.session),
])
```

controlled/bootstrap 阶段如果也希望立刻可见：

```js
const keep = new Set([...bootstrapTools, ...RESIDENT_LOCAL_TOOLS])
```

并可在 `dev-tool-search.mjs` 的能力索引里加入：

```js
'openviking_find / openviking_grep / openviking_read — OpenViking local memory/context search and read-only retrieval'
```

## 验证

1. `node --check` 检查改过的 `.mjs`。
2. 完全重启 EAC：`taskkill /IM "Deepseek Harness EAC.exe" /T /F` 后用 `explorer.exe "E:/Deepseek Harness EAC/Deepseek Harness EAC.exe"` 启动。
3. 日志确认：
   - `dsh web: http://127.0.0.1:<port>`
   - wrapper registered 日志出现。
4. 新建 DSH 会话，让模型列工具名，确认三项出现。
5. 用只读查询验证，例如：
   - `openviking_grep` 搜索一个已知 marker
   - `uri=viking://user`
   - 不允许用 bash 代替。

## Pitfalls

- 只改 `web` profile 没用；EAC 桌面通常跑 `web-desktop`。
- 官方 OpenViking recall 生效不代表 MCP 工具会暴露给模型。
- Host log 里的 `registered` 只证明进入 registry，不证明通过当前 preset 的最终 catalog 过滤。
- DSH `anchored-standard` 的最小 resident 工具集是有意设计；给 OpenViking 开洞时要只加只读工具，避免把写入/删除类 MCP 工具常驻暴露。
- 改本地 source 后要重新打包/安装，或明确复制到已安装 `node_modules`；否则 EAC 仍跑旧 tarball。