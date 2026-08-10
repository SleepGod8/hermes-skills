# 飞书导入（写入）详细配方（references/import.md）

实战来源：42 篇 Markdown/raw JSON 导入飞书云文档（2026-08-10 验证）。方案 B 全流程可用，无需额外权限。

## API 路径表（均经 lark_oapi SDK 源码确认）

| 操作 | Method + Path | 说明 |
|---|---|---|
| 拿 token | POST `/open-apis/auth/v3/tenant_access_token/internal` | body `{app_id, app_secret}` → `tenant_access_token` |
| 创建文档 | POST `/open-apis/docx/v1/documents` | body `{title}` → `data.document.document_id` |
| 获取根块 | GET `/open-apis/docx/v1/documents/{id}/blocks?page_size=500` | 根块 `block_type == 1`（page） |
| Markdown→块 | POST `/open-apis/docx/v1/documents/blocks/convert` | body `{content_type:"markdown", content}` → `data.blocks`（**需额外权限**） |
| 写入子块 | POST `/open-apis/docx/v1/documents/{id}/blocks/{root}/children` | body `{children:[Block...]}` |
| 删除文档 | DELETE `/open-apis/drive/v1/files/{token}?type=docx` | **必须带 ?type=docx**，否则 99992402 |
| 列知识空间 | GET `/open-apis/wiki/v2/spaces?page_size=20` | 只读权限可调，但空=应用非空间成员 |
| 创建空间 | POST `/open-apis/wiki/v2/spaces` | 需 `wiki:wiki` 写权限 |

## 权限矩阵（实测，tenant_access_token）

| 能力 | 所需 scope | 应用默认状态 |
|---|---|---|
| 拿 token | - | ✅ |
| 创建/读 docx | `docx:document` | ✅（能建文档、写块） |
| Markdown→块 | `docx:document.block:convert` | ❌ 报 99991672 Access denied，给申请链接 |
| 列知识空间 | `wiki:wiki:readonly` | ✅（空列表） |
| 建空间/移动节点 | `wiki:wiki` | ❌ 报 99991663 Invalid access token |
| 删云文档 | `drive:drive`? | ✅ 实测可删 |

结论：**方案 B（手动构造 blocks）只需 `docx:document`，是默认路径**；convert（方案 A）和 wiki 移动需要用户去开放平台开权限。

## docx Block 构造（方案 B）

block_type：1=page、2=text、3-6=heading1-4、12=bullet、14=code、15=quote、25=divider

Text 元素（支持简单行内格式）：
```json
{"text_run": {"content": "文本", "text_element_style": {"bold": true}}}  // **bold**
{"text_run": {"content": "代码", "text_element_style": {"inline_code": true}}}  // `code`
```

Block 示例：
```json
// 二级标题（heading2）
{"block_type": 4, "heading2": {"elements": [{"text_run": {"content": "1 Milvus简介"}}]}}
// 正文
{"block_type": 2, "text": {"elements": [{"text_run": {"content": "正文"}}]}}
// 列表项
{"block_type": 12, "bullet": {"elements": [{"text_run": {"content": "项目"}}]}}
// 代码块（language: 2=Python, 1=plain）
{"block_type": 14, "code": {"elements": [{"text_run": {"content": "print(1)"}}], "style": {"language": 2}}}
// 引用
{"block_type": 15, "quote": {"elements": [{"text_run": {"content": "来源..."}}]}}
// 分割线
{"block_type": 25}
```

raw 抓取数据 [cls, text] → docx Block 映射：
- `h1→3/heading1`、`h2→4/heading2`、`h3→5/heading3`、`h4→6/heading4`
- `b→12/bullet`（去开头的 •·-）
- `c→14/code`（先 `extract_code_text` 去「代码块XXX复制」噪音；python 检测：文本前 30 字符含 'python'/'py' → language 2）
- `t→2/text`；`image` 跳过；空文本跳过

## 批量导入注意

- children create 每批 40-50 块 + 0.2s 间隔（避免请求过大/限流）
- 空 raw（[]）直接跳过，不建空壳
- 大量文档（42 篇）前台命令会超时（600s 上限）→ 分两批或后台跑（terminal background + notify_on_complete）
- 测试文档用 `DELETE ...?type=docx` 清理
- 导入到云空间后，因无 `wiki:wiki`，文档在「我的空间」；用户可手动拖入知识库，或后续开权限后用 `wiki.v2.spaceNode.moveDocsToWiki` 批量移动

## 发现 API 路径的技巧

飞书开放平台文档是 SPA，curl 抓不到内容。最快路径：
```bash
pip install lark-oapi --no-deps
grep -rn "uri = " <site-packages>/lark_oapi/api/docx/v1/model/*.py
```
SDK 模型文件里每个 Request 都带 `http_method` + `uri` + `token_types`，一查即得。
