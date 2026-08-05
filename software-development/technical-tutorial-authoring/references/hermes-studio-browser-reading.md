# 使用 Hermes Studio 内置浏览器读取飞书/云文档

当用户在 **Hermes Studio 桌面版内置浏览器** 中已经打开了文档（已登录、有权限）时，优先用 `hermes_studio_browser_toolset`（MCP 工具集）读取当前标签页，而不是独立的 browser 工具。独立 browser 工具是另一套会话，拿不到用户已登录的标签页。

## 工具集三步走：list → describe → call

每次调用 `hermes_studio_browser_toolset` 都要显式给 `action` 参数：

1. `action=list` — 发现操作目录（tabs / navigate / snapshot / read_text / interact / screenshot / console）
2. `action=describe` + `tool=<精确工具名>` — 查看该工具的 inputSchema（参数格式）
3. `action=call` + `tool=<工具名>` + `arguments={...}` — 真正执行

## 关键操作与参数

### tabs（列出标签页）
- `arguments={"action": "list"}` → 返回 `activeTabId` + `tabs[]`（每项含 id/title/url）
- ⚠️ **坑**：`arguments` 为空或缺少 action 时直接报错 `{"error": "Invalid browser tab action"}`。必须先 describe 再 call。

### snapshot（页面快照）
- `arguments={"tab_id": "..."}` → 返回 `snapshotId` + `nodes[]`（每节点有 ref 如 @e40）+ 汇总 `text`
- 文本内容在 StaticText 节点的 `name` 字段里；链接是 `link` 节点
- 快照是**有界**的（只含视口附近节点），长文档必须滚动多次才能拿全

### read_text（读文本）
- 参数：`tab_id` + `snapshot_id`（必须最新）+ `ref` + `limit`（最大 20000）
- ⚠️ **坑**：对 `RootWebArea`（@e1）和 `Iframe` 节点调用返回空文本（`totalLength: 0`）。正确做法是读具体节点（heading / StaticText / link），或直接从 snapshot 返回的 `text` 字段汇总——飞书正文在 iframe 里，但快照仍能通过 StaticText 节点拿到文本。

### interact（滚动/按键）
- `arguments={"action": "scroll", "direction": "down", "pixels": 800, "tab_id": "..."}`
- 也可 `{"action": "press", "key": "End"}` 跳到底部
- 滚动后必须重新 snapshot（ref 会变，旧 snapshotId 会被拒绝）

### screenshot（截图验证）
- 返回 `MEDIA:<本地png路径>`，配合 `vision_analyze` 确认页面是否正常渲染、内容是否完整

## 飞书文档读取流程

1. `tabs` action=list → 记录 `activeTabId`
2. `snapshot` → 从 `text` 字段提取可见文本
3. 循环：`interact` scroll down（800~900px）→ `snapshot`，直到连续两次快照内容相同（=已到底部）
4. 汇总所有快照的 StaticText / link 文本，按章节标题重组
5. 截图 + vision 检查是否有懒加载内容漏读

## 注意事项

- 滚动后节点 ref 会变，**必须用最新 snapshotId**
- 两次快照内容完全一样 = 到底部或滚动未生效，可换 press End 再试
- 飞书正文在 iframe 里，read_text 读 iframe 返回空属正常，不代表内容缺失
- 提取的文本中会出现大量空白 StaticText（`​`），整理时过滤掉
- 文档若含代码块，快照只给"代码块"占位 + 按钮（Plain Text/复制），完整代码需点击展开或另行处理
