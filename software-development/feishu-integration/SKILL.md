---
name: feishu-integration
description: "飞书/Lark 平台接入 Hermes/Agent：知识库(wiki)检索、云文档(docx)只读、官方 lark-openapi-mcp 配置与权限。Use when 用户要接入飞书知识库增强编程/多agent / 读取飞书文档 / 配置 lark-mcp / 问飞书API可行性。"
version: 1.0.0
tags: [feishu, lark, mcp, wiki, docx, knowledge-base, openapi]
platforms: [windows]
---

# 飞书/Lark 平台集成（知识库 + 云文档 + MCP）

接入飞书知识库/云文档到 Hermes 或 agent 工作流的完整路径。2026-08-10 调研结论：**完全可行**，官方 MCP 原生支持 wiki 搜索 + docx 只读。用户当时选择暂缓实施；再提「接入飞书知识库」时从「实施路径」直接开始。

## 触发条件

- 用户要连接飞书知识库（wiki）来增强编程能力 / 多 agent 协作
- 要读取飞书云文档内容（docx 纯文本）
- 配置 `lark-mcp` / 问「飞书 API 能不能做 X」
- 用户飞书 bot 已接入（feishu adapter / 群聊女仆），应用凭证在 `$HERMES_HOME/.env` 的 `FEISHU_APP_ID` / `FEISHU_APP_SECRET`

## 核心事实

- 官方 MCP：`larksuite/lark-openapi-mcp`（npm `@larksuiteoapi/lark-mcp`，**Beta**）
- 官方文档：https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/mcp_integration/mcp_introduction
- 需 Node.js（用户本机 v24.18.0 + npx 已装）
- 限制：**不支持文档编辑**（只读+导入）、**不支持文件上传下载**

## 配置（Hermes stdio MCP）

```bash
printf 'n\ny\n' | hermes mcp add lark --command "npx -y @larksuiteoapi/lark-mcp mcp -a <app_id> -s <app_secret>"
# 国际版加 --domain https://open.larksuite.com
# 用户身份加 --oauth --token-mode user_access_token（需先 npx ... login，重定向 URL http://localhost:3000/callback）
```

标准 MCP 规则：新 server 需新会话 `/reset` 加载工具；`hermes mcp test lark` 验证。

## 知识库相关工具

| 工具 | 用途 |
|------|------|
| `wiki.v1.node.search` | 搜索知识库节点 |
| `wiki.v2.space.list` | 有权限的知识空间列表 |
| `wiki.v2.space.get` / `getNode` | 空间/节点信息 |
| `wiki.v2.spaceNode.list` | 遍历节点树（分页） |
| `docx.v1.document.rawContent` | **读文档纯文本（核心）** |
| `docx.v1.document.get` / `documentBlock.list` | 文档信息 / 块级内容 |

默认只启用常用预设；自定义用 `-t` 逗号分隔（完整工具表在仓库 `docs/reference/tool-presets/`）。

## 权限（最大门槛，需用户在开放平台操作）

1. 开发者后台 → 应用 → 权限管理 → 加 `wiki:wiki:readonly` + `docx:document:readonly`（多维表格再 `bitable:app:readonly`）
2. **发布新版本**才生效
3. **关键坑：应用身份（tenant_access_token）访问 wiki 时，应用/机器人必须是知识空间的成员**——知识库非全员可读时要把机器人加为成员，否则 API 返回空/无权限

## 三档增强方案

- **实时 MCP 检索**：lark-mcp 直连按需搜索+读文档 → 最快见效，适合知识库不大
- **本地 RAG 索引**：定时导出 markdown → 切块 → bge-m3（Ollama）→ Milvus。用户已有 `D:\w1_d3` RAG 教学代码 + Milvus + Ollama 直接复用；无 API 延迟/配额焦虑
- **多 Agent 共享**：各 agent（女仆档案/OpenCode/Codex）共用 lark-mcp 或共享本地 RAG → 团队规范/架构决策/API 约定统一注入，多 agent 开发一致性强（收益最大）

## 坑与注意

- 现有飞书 bot 应用大概率只有消息权限，需补 wiki/docx 读权限
- MCP 是 Beta，功能可能变更
- recall-mcp（同仓库另一 MCP）：检索**飞书开放平台自己的开发文档**（写飞书集成代码有用），**不是用户知识库**——别混用
- 国内网络：raw.githubusercontent 直连常失败；git clone 用 `git -c http.proxy= -c https.proxy= clone ...` 直连 GitHub

## 实施路径（用户决定动手时）

1. 用户：开放平台加权限 → 发布版本 → 把机器人加进知识库成员
2. 执行 `hermes mcp add lark`（用 .env 的 app_id/app_secret）
3. 新会话验证工具 → 实测 `wiki.v1.node.search` + `docx.v1.document.rawContent`

## 相关

- MCP 通用配置/排障：`hermes-mcp-configuration` skill（注意：该技能为手动创建，后台 curator 不可改）
- 飞书 bot adapter 补丁（群聊 @ 规则）：`feishu-smart-mention-patch` skill
- 群聊自主沟通协议：`group-chat-autonomous-chat` skill
