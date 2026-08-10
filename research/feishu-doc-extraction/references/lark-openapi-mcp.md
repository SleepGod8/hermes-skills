# 飞书官方 OpenAPI MCP（lark-openapi-mcp）调研笔记

> 调研日期 2026-08。仓库 `larksuite/lark-openapi-mcp`（npm 包 `@larksuiteoapi/lark-mcp`），官方 Beta。
> 用途：把飞书开放平台 API 封装为 MCP 工具——文档处理、知识库、多维表格、消息等。「把飞书知识库接入 Hermes 提高编程能力 / 多 agent 共享知识」的正规通道。

## 安装/配置（stdio）

```json
{
  "mcpServers": {
    "lark-mcp": {
      "command": "npx",
      "args": ["-y", "@larksuiteoapi/lark-mcp", "mcp", "-a", "<app_id>", "-s", "<app_secret>"]
    }
  }
}
```

- Hermes 接入：`hermes mcp add lark --command "npx -y @larksuiteoapi/lark-mcp mcp -a <id> -s <secret>"`（stdio；交互提示需 piped 输入 `printf 'n\ny\n' |`）
- 用户环境（2026-08 已验证）：`.env` 已有 `FEISHU_APP_ID` / `FEISHU_APP_SECRET`（飞书 bot 应用），Node v24 + npx 11 已装
- 可用 `-t` 参数只启用指定工具/preset；`--domain` 切换国际版；`--oauth` + `--token-mode user_access_token` 走用户身份

## 知识库（wiki）读取工具

- `wiki.v1.node.search` — 搜索知识库节点
- `wiki.v2.space.list` / `wiki.v2.space.get` — 空间列表/信息
- `wiki.v2.space.getNode` / `wiki.v2.spaceNode.list` — 节点信息/子节点
- `wiki.v2.spaceNode.create` / `wiki.v2.spaceNode.move` / `wiki.v2.spaceNode.moveDocsToWiki` — 写入/移动

## 文档（docx）工具

- 读：`docx.v1.document.rawContent`（纯文本）、`docx.v1.documentBlock.list` / `documentBlockChildren.get`（块内容）
- 写：`docx.v1.document.create`、`docx.v1.document.convert`（Markdown/HTML→块，导入内容核心）、`docx.v1.documentBlockChildren.create`
- 其他：`drive.v1.exportTask.create/get`（导出为文件）、`drive.v1.importTask.create/get`（导入本地文件）

## 多维表格（bitable）工具——飞书的"数据库"

- 查：`bitable.v1.appTableRecord.search` / `list` / `get`（单次最多 500 行，支持分页）、`bitable.v1.appTable.list`、`bitable.v1.appTableField.list`
- 写：`bitable.v1.appTableRecord.create` / `batchCreate`

## 权限要求（应用后台，发布版本后生效）

- 读知识库：`wiki:wiki:readonly` + `docx:document:readonly`
- 写知识库：`wiki:wiki` + `docx:document` + `drive:drive`
- 多维表格：`bitable:app:readonly` / `bitable:app`
- **机器人（应用）必须是知识空间成员/协作者**，否则 API 403；私有知识库需把应用加为成员

## 导入知识库全流程（读→转→建→移）

1. 读源文档：`rawContent` 或导出 Markdown（保格式）
2. 转换：`docx.v1.document.convert`（Markdown→块）
3. 建文档：`docx.v1.document.create`
4. 移入：`wiki.v2.spaceNode.moveDocsToWiki`
   或直接 `wiki.v2.spaceNode.create` 在知识库建节点（obj_type=docx）

## 坑

- MCP 官方标注 Beta，功能可能变更
- Hermes 新 MCP server 需要**新会话 /reset** 才加载工具（启动时发现，无热加载）
- **MCP 是 per-profile**：给 default 配了 ≠ 群聊其他 agent 有；群聊每个 agent 的 Profile 有独立 `config.yaml`（抽查 aphrodite/ares/artemis 等确认各自有 mcp_servers 块）
- 群聊 @all N 个 agent = N 份上下文 + N 路 API 并发，注意飞书限流；推荐「知识官」agent 专职查询（方案 C），其他 agent @ 它拿资料
- 读取"别人的文档"：应用只能读自己可见的文档；分享链接若设密码/私有，先走浏览器提取（见 SKILL.md 主流程）
