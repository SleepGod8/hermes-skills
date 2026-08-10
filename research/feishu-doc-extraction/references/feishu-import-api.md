# 飞书导入 API 参考（2026-08 实测）

## 认证

```
POST /open-apis/auth/v3/tenant_access_token/internal
body: {"app_id": "<FEISHU_APP_ID>", "app_secret": "<FEISHU_APP_SECRET>"}
→ data.tenant_access_token（有效期约 2 小时）
```
凭证位置：`C:/Users/<user>/AppData/Local/hermes/.env`（FEISHU_APP_ID / FEISHU_APP_SECRET）

## 权限 scope 矩阵（实测）

| scope | 用途 | 常见状态 |
|---|---|---|
| `docx:document` | 建文档、读块、写子块 | ✅ 通常已有 |
| `wiki:wiki:readonly` | 列知识空间 | ✅ |
| `wiki:wiki` | 创建空间/节点、moveDocsToWiki | 需用户开放平台补 |
| `docx:document.block:convert` | Markdown/HTML→文档块 | ❌ 常缺 → Plan B |
| `contact:contact.base:readonly` 等 | 手机号/邮箱查 open_id | ❌ 常缺 |
| `tenant:tenant:readonly` | 查租户域名 | ❌ 常缺 |
| `drive:drive` | 文件夹/元数据管理 | 视应用 |

错误码 `99991672 Access denied` → 错误 JSON 的 `error.permission_violations[].subject` 给出缺失 scope，且自带开放平台申请链接：`https://open.feishu.cn/app/<app_id>/auth?q=<scope>...`，可直接转给用户点。
错误码 `99992402 field validation failed` → 多为路径缺查询参数（如 `?type=docx`）或 body 字段名错。

## docx Block 类型速查

```
1=page  2=text  3=heading1  4=heading2  5=heading3  6=heading4
7-11=heading5-9  12=bullet  13=ordered  14=code  15=quote  25=divider
```

Block 构造（children create 的 body 元素）：
```json
{"block_type": 2, "text": {"elements": [{"text_run": {"content": "正文"}}]}}
{"block_type": 4, "heading2": {"elements": [{"text_run": {"content": "标题"}}]}}
{"block_type": 12, "bullet": {"elements": [{"text_run": {"content": "列表项"}}]}}
{"block_type": 14, "code": {"elements": [{"text_run": {"content": "代码"}}], "style": {"language": 1}}}
```
- 内联样式：`text_element_style: {"bold": true}` 或 `{"inline_code": true}`
- code 语言：1=plain/text，2=python（枚举值以 API 文档为准）

## API 路径表

| 操作 | 方法 + 路径 |
|---|---|
| 建文档 | POST `/open-apis/docx/v1/documents` `{title, folder_token?}` → `data.document.document_id` |
| 列块 | GET `/open-apis/docx/v1/documents/{id}/blocks?page_size=500` → 根块 block_type==1 |
| 写子块 | POST `/open-apis/docx/v1/documents/{id}/blocks/{root}/children` `{children:[...]}` |
| Markdown转块 | POST `/open-apis/docx/v1/documents/blocks/convert` `{content_type:"markdown", content}` → `data.blocks`（**路径不是** `/{id}/convert`） |
| 设公开权限 | PATCH `/open-apis/drive/v1/permissions/{token}/public?type=docx` `{link_share_entity:"tenant_editable", link_perm:"edit"}` |
| 删文档 | DELETE `/open-apis/drive/v1/files/{token}?type=docx` |
| 列应用空间文件 | GET `/open-apis/drive/v1/files?page_size=100` |
| 列知识空间 | GET `/open-apis/wiki/v2/spaces` |
| 文档 meta（url 常为空） | POST `/open-apis/drive/v1/metas/batch_query` |

## 关键坑（实测）

1. **应用云空间归属**：应用身份创建的文档在应用空间，用户个人空间看不到。必须设 `tenant_editable` 公开权限后用户才能通过链接/搜索访问。
2. **空间成员**：应用有 wiki:wiki 权限但 `wiki/v2/spaces` 仍返回空 → 应用不是任何空间成员。让用户在目标知识空间 设置→成员管理→添加应用机器人。
3. **文档链接域名**：`https://<租户域名>.feishu.cn/docx/<token>`；租户域名 API 拿不到（tenant scope 缺）→ 让用户从任意飞书文档 URL 取，或直接搜标题。
4. 批量导入 42 篇约 8 分钟，前台 600s 超时 → 后台运行。
5. 重复导入检测：列应用空间用 `Counter(name)` 找重名。
6. 标题中文乱码是终端 GBK 显示问题，实际数据正常。
