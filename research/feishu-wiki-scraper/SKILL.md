---
name: feishu-wiki-scraper
description: 飞书知识库(Wiki)/云文档全文抓取到本地 Markdown 的完整方案。覆盖密码解锁、页面内部 API 拿目录树、Canvas 虚拟列表滚动收集、长文分段取回、Python 清洗。Use when 用户想把飞书分享文档/知识库导入本地或自己的知识库 / 抓取飞书文档正文。
version: 1.0.0
tags: [feishu, wiki, scraper, canvas, virtual-list, markdown]
---

# 飞书知识库/云文档抓取方案

> 2026-08-10 实战验证：抓取「AI项目603」知识库 43 篇文档全流程跑通
> 场景：用户看到别人的飞书文档/知识库内容有价值，想导入自己知识库或存本地

## 触发条件

- 用户给飞书 wiki/docx 分享链接，想抓取内容
- 用户想把飞书知识库批量导入本地/自己的知识库
- 飞书文档内容在 accessibility snapshot 里看不到（Canvas 渲染）

## 核心事实（踩坑总结）

1. **飞书正文是 Canvas + 虚拟列表渲染**：DOM 里只有视口附近的块，accessibility 快照只能看到少量文本，必须 JS 滚动收集
2. **密码保护**：分享链接可能带「请输入密码访问」，需 browser_type + browser_click 解锁；解锁 cookie 会话内延续，子文档直接可看
3. **知识库目录树**：页面内部 API 可拿（无需额外鉴权，浏览器 cookie 就行）：
   `GET https://<tenant>.feishu.cn/space/api/wiki/v2/tree/get_info/?space_id=<sid>&with_space=true&with_perm=true&expand_shortcut=true&need_shared=true&exclude_fields=5&with_deleted=true&wiki_token=<root_token>`
   返回 `data.tree.child_map[token] = [子节点]` + `data.tree.nodes[token] = {title, obj_token, url, has_child}`
   - 必须**在知识库首页（根节点页面）**调用才返回完整树；在子文档页面调用返回空
   - 递归遍历所有 has_child 节点可拿完整多层目录树（文件夹嵌套）
4. **正文不走 REST API**（docx 内容走 websocket），只有 `/space/api/meta/` 可用。必须靠 DOM 渲染
5. **空文档判断**：收集脚本返回 n=0 / blocks 空 = 空文档（用户可能提前知道哪些是空的）

## 标准收集脚本（增强版）

在 browser_console 执行（导航到文档后等加载）：

```js
(async () => { await new Promise(r => setTimeout(r, 2000));
  const scroller = document.querySelector('.bear-web-x-container') || document.scrollingElement;
  if (!scroller) return JSON.stringify({n:0, reason:'no-scroller'});
  scroller.scrollTop = 0; window.__blocks = []; const seen = new Set();
  const collect = () => { document.querySelectorAll('[data-block-id]').forEach(el => {
    const cls = (el.className || '').toString();
    if (/docx-page-block|docx-view-block|docx-file-block/.test(cls)) return; // 跳过容器块
    const t = (el.textContent || '').replace(/\u200b/g, '').replace(/\u200e/g, '').trim();
    if (!t) return; if (seen.has(t)) return; seen.add(t);
    let c = 't';
    if (cls.includes('heading2')) c = 'h2'; else if (cls.includes('heading3')) c = 'h3';
    else if (cls.includes('heading4')) c = 'h4'; else if (cls.includes('bullet')) c = 'b';
    else if (cls.includes('code')) c = 'c';
    window.__blocks.push([c, t]); }); };
  await new Promise(r => setTimeout(r, 500)); collect();
  let lastY = -1, guard = 0;
  while (guard < 150) { guard++; scroller.scrollTop += scroller.clientHeight * 0.9;
    await new Promise(r => setTimeout(r, 150)); collect();
    if (scroller.scrollTop === lastY && guard > 5) break; lastY = scroller.scrollTop; }
  scroller.scrollTop = scroller.scrollHeight; // 强制滚到底兜底
  await new Promise(r => setTimeout(r, 500)); collect();
  const chars = window.__blocks.reduce((a,b)=>a+b[1].length,0);
  return JSON.stringify({n: window.__blocks.length, chars, tooBig: chars > 24000}); })()
```

- 块类型 cls 编码：`h2/h3/h4` 标题、`b` 列表、`c` 代码块、`t` 正文
- 代码块 textContent 含 UI 噪音「代码块XXX复制」，清洗时正则提取

## 长文分段取回（>24k 字符会截断返回）

```js
(() => JSON.stringify(window.__blocks.slice(0,280)))()   // 每段 280 块
(() => JSON.stringify(window.__blocks.slice(280,560)))()
// ...直到取完（用 n 判断段数）
```
每段 write_file 存 `<名>_partN.json`，最后 Python 合并（json.load + extend + ensure_ascii=False），删 part。

## 批量清洗 → Markdown

见实战脚本 `C:/Users/80704/AppData/Local/hermes/workspace/feishu_import/build_markdown.py`：
- h2/h3/h4 → ##/###/####
- b → `- `（去 • 前缀）
- c → ```代码块（语言映射 python/java→bash/go→bash/markdown→yaml/xml→xml）
- 空文档生成占位 md

## 多 Agent 并行加速

43 篇全量抓取时用 delegate_task 并行：3 个子 agent 各 5-8 篇，context 里给「收集脚本 + 密码 + 落盘路径 + 分段规则 + 返回格式」。子 agent 浏览器会话共享解锁 cookie，无需重复输密码。坑：子 agent 可能达到工具调用上限，返回部分完成，需检查 part 文件残留并补抓。

## 导入自己知识库（写入侧）

官方 MCP `@larksuiteoapi/lark-mcp`（npx -y 运行）支持：wiki.v2.spaceNode.create / docx.v1.document.create / docx.v1.document.convert(Markdown→块) / wiki.v2.spaceNode.moveDocsToWiki。前提：应用加 wiki/docx/drive 权限 + 发布版本 + 机器人是知识库成员。

## Pitfalls

- 首次收集脚本 guard=60 会漏长文尾部（有文档 50000px 高，只滚到 26760px）→ 必须 guard=150 + 强制滚到底
- browser_console 返回超过 ~24k 字符会截断，长文必须分段
- get_info 目录 API 只在知识库首页页面生效
- 密码页每次回到首页可能要求重新输入（cookie 作用域限制）
- 图片块 textContent 为空，内容会丢（格式保真有限）
