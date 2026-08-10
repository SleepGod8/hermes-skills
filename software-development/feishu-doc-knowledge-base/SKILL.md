---
name: feishu-doc-knowledge-base
description: "飞书/Lark 文档与知识库的提取（读取）与导入（写入）：密码解锁、内部目录树 API、Canvas 虚拟列表 DOM 滚动收集、超长文档分段取回、docx 直链绕过登录墙；导入用 docx API 手动构造 blocks（方案 B，无需额外权限）。Use when 抓取飞书分享文档/知识库、把 Markdown 或抓取内容导入飞书、飞书知识库迁移、读取他人飞书文档。"
version: 1.0.0
tags: [feishu, lark, wiki, docx, extraction, import, canvas, virtual-list, api, knowledge-base]
---

# 飞书文档/知识库 提取与导入

> 版本：v1.0 | 2026-08-10 | 在「AI项目603」知识库全量抓取（42篇/81万字）+ 飞书导入实战中验证

## 触发条件

- 用户要抓取/复制他人分享的飞书文档、知识库（Wiki）内容到本地
- 用户要把本地 Markdown / 抓取的资料导入飞书云文档或知识库
- 飞书知识库迁移、批量搬运、内容备份
- 读取「获得链接的人可阅读」或带密码的飞书文档

## 前置条件

- 飞书应用凭证：`%LOCALAPPDATA%\hermes\.env` 里的 `FEISHU_APP_ID` / `FEISHU_APP_SECRET`（现有 bot 应用即可）
- 密码保护的知识库需要分享者提供的访问密码
- 应用权限（决定读取/写入能力，详见 references/import.md 权限矩阵）：
  - 提取只读场景：浏览器有登录态/密码即可，应用权限非必需
  - 导入场景：`docx:document` 够用（方案 B）；`docx:document.block:convert` + `wiki:wiki` 可全自动（方案 A）

## 一、提取（读取）流程

### 1. 密码解锁（wiki 首页需要）
1. `browser_navigate` 打开 wiki 链接 → 若出现「请输入密码访问」输入框
2. `browser_type` 输入密码 → `browser_click` 确定按钮
3. 密码 cookie 延续到同空间子文档；但**回首页可能又要重新输入**

### 2. 获取完整目录树（页面内部 API）
在浏览器 console 中 fetch（带登录 cookie）：
```
/space/api/wiki/v2/tree/get_info/?space_id=<sid>&with_space=true&with_perm=true&expand_shortcut=true&need_shared=true&exclude_fields=5&with_deleted=true&wiki_token=<root>
```
返回 `data.tree.child_map`（父→子 token 映射）+ `data.tree.nodes`（节点详情：title/obj_token/obj_type/url/has_child）。**必须递归遍历**（文件夹可嵌套 4+ 层：优秀项目参考→金融→产品立项书→AI投顾案例）。space_id 从首个 get_info 响应的节点里拿。
> 注意：在子文档页面调用 get_info 可能返回空 child_map —— 先导航回知识库根页面再调。

### 3. 文档正文：不能走 REST，必须 DOM 收集
docx 正文通过 websocket/pandora 传输，REST 探测（`/space/api/docx/...`、`/space/api/meta/`）拿不到正文。正文渲染在 DOM 里，且是**虚拟列表**（只渲染视口附近，滚动时旧节点被回收）。可靠方法：滚动 + 块级收集（详见 references/extraction.md 的完整 JS 脚本）：
- 滚动容器：`document.querySelector('.bear-web-x-container')`（或 document.scrollingElement）
- 收集粒度：`[data-block-id]` 叶子块，跳过容器类 `docx-page-block|docx-view-block|docx-file-block`
- 分类：`heading2-/heading3-/heading4-` 标题、`text-` 正文、`bullet-` 列表、`code-` 代码块、`image-` 图片（空文本跳过）
- 去重：seen-set 按文本；**边滚边存 `window.__blocks`**，不直接返回（防截断）
- 长文 >24k 字符：分 280 块/段取回（`window.__blocks.slice(0,280)` 等），写 part 文件后合并
- 滚动参数：0.8×视口 + 180ms；**guard 上限要够（60-150）**，最后强制 `scrollTop = scrollHeight` 再收集一次兜底尾部

### 4. 登录墙文档的绕过：docx 直链
部分文档（独立分享、组织内可见）用 wiki URL 会跳 `accounts.feishu.cn` 登录页（扫码）。**改用 `https://ocnlg5l4bjoh.feishu.cn/docx/<obj_token>` 直链**可绕过（会 302 到 wiki 页但直接显示内容）。obj_token 从目录树节点的 `obj_token` 拿。

### 5. 并行加速
delegate_task 派 3 个子 agent 并行抓（浏览器会话/cookie 共享，密码只需主会话解锁一次）。context 里给：密码、收集脚本、落盘路径 `feishu_import/raw/<名>.json`、超长分段规则、返回格式（只回状态摘要不回正文）。子 agent 抓完注意检查 part 文件是否齐全、是否被登出中断。

### 6. 清洗成 Markdown
- 去零宽字符 `\u200b\u200e\ufeff`、全角空格
- 代码块内 UI 噪音：`代码块XXX复制` → 提取真实代码（正则 `代码块\s*(.*?)复制\s*(.*)$`），语言映射（python/java/go/markdown→yaml/xml）
- 批量脚本参考 workspace `feishu_import/build_markdown.py`（兼容 list 和 dict 两种 block 格式）

## 二、导入（写入）流程

**推荐方案 B（手动构造 docx blocks）—— 只需 `docx:document` 权限，实测全流程可用。**
API 路径、权限矩阵、block_type 映射详见 `references/import.md`；可运行脚本 `scripts/import_feishu.py`。

核心链路：
1. `POST /open-apis/auth/v3/tenant_access_token/internal` 拿 token（app_id/app_secret）
2. raw blocks（[cls, text]）→ docx Block 数组（heading2→block_type 4 等）
3. `POST /open-apis/docx/v1/documents` 创建文档（拿 document_id）
4. `GET /open-apis/docx/v1/documents/{id}/blocks` 拿根块（block_type=1）
5. `POST /open-apis/docx/v1/documents/{id}/blocks/{root}/children` 分批写内容（每批 40 块 + 0.2s 间隔）
6. 清理测试文档：`DELETE /open-apis/drive/v1/files/{token}?type=docx`

## Pitfalls

- **零宽空格**：从微信/网页复制命令会带入 U+200B → docker 报 `invalid reference format`。验证：`('cmd').Length` 或转储字节；解决：手敲
- **convert 权限**：`/docx/v1/documents/blocks/convert`（Markdown→blocks）需要 `docx:document.block:convert`，应用默认没有；方案 B 完全绕开它
- **wiki 写权限**：`wiki:wiki` 缺失时无法创建空间/节点/移动文档；文档会落在云空间，用户可在 UI 里手动拖入知识库
- **导入空文档**：raw json 为空数组直接跳过，别创建空壳
- **API 路径别猜**：官方文档是 SPA 难抓 → `pip install lark-oapi` 后 grep `api/docx/v1/model/*.py` 里的 `uri = "..."` 是最快的确路径方法
- **删除接口**：`DELETE /drive/v1/files/{token}` 必须带 `?type=docx`，否则 field validation failed
- **子 agent 会改共享脚本**：并行任务后检查 build/merge 脚本是否被改动（本次子 agent 给 build_markdown.py 加了 SKIP 集合）

## 相关

- 官方 MCP：`@larksuiteoapi/lark-mcp`（larksuite/lark-openapi-mcp），支持 wiki/docx/bitable 读写，可经 `hermes mcp add` 接入（见 hermes-mcp-configuration）
- 飞书消息/adapter 相关（群聊、mention）→ feishu-smart-mention-patch
- 其他受限文档提取（腾讯文档 textPool 解码）→ restricted-doc-extraction / canvas-doc-extraction
