---
name: feishu-doc-import
description: "飞书分享文档/知识库全流程：密码解锁→目录树API→虚拟列表滚动收集→blocks转Markdown→应用API导入飞书(手动构造blocks绕过convert权限)→transfer owner给用户。Use when 抓取飞书文档 / 导入飞书知识库 / 分享链接提取内容。"
version: 1.0.0
tags: [feishu, wiki, docx, extraction, import, api]
---

# 飞书文档抓取 + 导入全流程

> 实战验证：2026-08 抓取「AI项目603」知识库 42 篇（81万字符）并导入飞书 AIcoding 空间。
> 脚本位置：`C:/Users/80704/AppData/Local/hermes/workspace/feishu_import/`（import_feishu.py / build_markdown.py / merge_parts.py）

## 触发条件

- 用户提供飞书分享链接（`xxx.feishu.cn/wiki/xxx` 或 `/docx/xxx`）要求提取/导入内容
- 把抓到的资料导入用户自己的飞书知识库

## 一、抓取（提取文档内容）

### 1. 密码解锁
打开 wiki 链接若显示「请输入密码访问」→ browser_type 输入密码 → browser_click 确定。

### 2. 目录树（页面内部 API，带 cookie）
```js
fetch('/space/api/wiki/v2/tree/get_info/?space_id=<sid>&with_space=true&with_perm=true&expand_shortcut=true&need_shared=true&exclude_fields=5&with_deleted=true&wiki_token=<root>', {credentials:'include'})
```
返回 `data.tree.child_map`（父→子token映射）+ `data.tree.nodes`（节点详情：title/obj_token/obj_type/has_child）。嵌套文件夹递归展开。

### 3. 正文收集（虚拟列表滚动）
飞书 docx 正文 Canvas 渲染、虚拟列表只渲染视口——必须滚动收集：
```js
(async () => { await new Promise(r=>setTimeout(r,2000));
const scroller=document.querySelector('.bear-web-x-container')||document.scrollingElement;
scroller.scrollTop=0; window.__blocks=[]; const seen=new Set();
const collect=()=>{ document.querySelectorAll('[data-block-id]').forEach(el=>{
 const cls=(el.className||'').toString();
 if(/docx-page-block|docx-view-block|docx-file-block/.test(cls)) return;  // 跳过容器
 const t=(el.textContent||'').replace(/\u200b/g,'').replace(/\u200e/g,'').trim();
 if(!t||seen.has(t)) return; seen.add(t);
 let c='t'; if(cls.includes('heading2'))c='h2'; else if(cls.includes('heading3'))c='h3';
 else if(cls.includes('heading4'))c='h4'; else if(cls.includes('bullet'))c='b';
 else if(cls.includes('code'))c='c'; window.__blocks.push([c,t]); }); };
await new Promise(r=>setTimeout(r,500)); collect();
let lastY=-1,guard=0;
while(guard<150){guard++; scroller.scrollTop+=scroller.clientHeight*0.9;
 await new Promise(r=>setTimeout(r,150)); collect();
 if(scroller.scrollTop===lastY&&guard>5)break; lastY=scroller.scrollTop;}
scroller.scrollTop=scroller.scrollHeight; await new Promise(r=>setTimeout(r,500)); collect();
return JSON.stringify({n:window.__blocks.length, chars:window.__blocks.reduce((a,b)=>a+b[1].length,0)});})()
```
- 返回 chars>24000 → 分段取回：`(()=>JSON.stringify(window.__blocks.slice(a,b)))()` 每段 ~280 块，写 part 文件后 Python 合并。
- **滚动要慢（0.9视口/150ms）**，快了会漏渲染；结束时强制滚到底兜尾。

### 4. 需登录的文档
独立分享链接（不在知识库空间内）会跳 `accounts.feishu.cn` 登录页。**用 docx 直链可绕过**：`https://<domain>.feishu.cn/docx/<obj_token>`。若仍要登录只能用户手动复制。

### 5. raw blocks → Markdown
build_markdown.py：h2→`##`、h3→`###`、b→`- `、c→代码块（提取「代码块XXX复制」真实代码 + 语言映射）、t→正文。dict 格式 `{cls:'heading2-',text}` 与 list 格式 `['h2',text]` 都要兼容。

## 二、导入（写入飞书）

### 权限探测（tenant_access_token）
```
POST /open-apis/auth/v3/tenant_access_token/internal {app_id,app_secret}
GET  /open-apis/docx/v1/documents/{id}          # 或直接 create 测试
```
- ✅ docx:document（create 文档）— 通常有
- ❌ docx:document.block:convert（Markdown转块）— **常缺** → 用 Plan B
- ❌ wiki:wiki 写权限 — 可能缺

### Plan B：手动构造 blocks（无需 convert 权限）
raw json → docx blocks：
- block_type: 2=text, 3-6=heading1-4, 12=bullet, 14=code, 15=quote
- text 结构：`{"block_type":2,"text":{"elements":[{"text_run":{"content":"..."}}]}}`
- heading：`{"block_type":4,"heading2":{"elements":[...]}}`
- code：`{"block_type":14,"code":{"elements":[{"text_run":{"content":code}}],"style":{"language":2}}}` (2=python)

### 导入流程（import_feishu.py）
1. `POST /open-apis/docx/v1/documents` `{"title":...}` → document_id
2. `GET  /open-apis/docx/v1/documents/{id}/blocks?page_size=500` → 根块 block_id
3. `POST /open-apis/docx/v1/documents/{id}/blocks/{root}/children` `{"children":[...]}` 每批 40 块

### ⚠️ 关键坑（务必执行）
1. **应用创建文档在「应用云空间」，用户登录看不到！** 必须：
   - `PATCH /open-apis/drive/v1/permissions/{token}/public?type=docx` `{"link_share_entity":"tenant_editable"}` → 组织内可编辑
   - `POST /open-apis/drive/v1/permissions/{token}/members/transfer_owner?type=docx` `{"member_type":"openid","member_id":<用户open_id>}` → **转移所有权给用户**（否则用户无移动/管理权限）
2. **用户 open_id 获取**：contact API 通常无权限 → 从群聊消息拿：`GET /open-apis/im/v1/chats` → `GET /open-apis/im/v1/messages?container_id_type=chat&container_id={chat}` 找 `sender_type=user` 的 `sender.id`
3. **move_docs_to_wiki 需要应用是目标空间成员**（`POST /open-apis/wiki/v2/spaces/{sid}/nodes/move_docs_to_wiki` body `{parent_wiki_token,obj_type:"docx",obj_token}`）。但知识空间「添加管理员」弹窗**只支持用户/群组/部门，不支持应用**；API spaceMember.create 也需空间权限（鸡生蛋）→ **只能用户手动移动**（云文档批量勾选→移动到知识空间）或改空间公开范围为组织所。
4. space_id 是**数字**；用户给的 `/wiki/<token>` 是节点 wiki_token，用 `GET /open-apis/wiki/v2/spaces/get_node?token={wiki_token}&obj_type=wiki` 反查 space_id。
5. 删除文档：`DELETE /open-apis/drive/v1/files/{token}?type=docx`（必须带 type=docx）
6. 文档链接：`https://{domain}.feishu.cn/docx/{token}`，域名用 `POST /open-apis/drive/v1/metas/batch_query`（body `{"request_docs":[{"doc_token":t,"doc_type":"docx"}],"with_url":true}`）返回的 url 拿。

## 三、批量操作

- 抓取用 delegate_task 并行（每个子 agent 5-8 篇，把收集脚本+密码放 context，要求落盘 raw/ 只回状态摘要）
- 导入用循环：每篇 create→blocks→children，40 块/批 + 0.2s 间隔；多篇 >10 分钟用 background + notify_on_complete

## 验证清单

- [ ] 应用 drive 空间文件数归 0（移动完成证据）
- [ ] 目标空间首页节点可查
- [ ] 用户云文档「我创建的」能看到文档
- [ ] convert 权限缺失时 Plan B blocks 正常渲染
