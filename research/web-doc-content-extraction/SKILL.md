---
name: web-doc-content-extraction
description: "从受限网页文档提取正文：腾讯文档(docs.qq.com)等 Canvas 渲染文档的页面内存对象提取法、登录墙/只读文档的可行与死路路径。与 technical-tutorial-authoring（飞书/语雀）互补——本技能专治『DOM 里没有文本』的文档。"
version: 1.0.0
author: agent
tags: [web-extraction, tencent-docs, docs.qq.com, canvas-rendered, browser, 腾讯文档, 文档提取]
platforms: [windows, macos, linux]
---

# Web 文档正文提取（Canvas 渲染 / 登录墙类）

## 触发条件

- 用户给出 docs.qq.com / 其他 Canvas 渲染文档链接，要求读取/研究/整理内容
- `browser_snapshot` 只拿到大纲和批注，正文 DOM 提取为空
- 文档允许只读查看（advPolicy.view_forbid_copy_print: 0）但正文拿不到

## 腾讯文档 (docs.qq.com) 提取法（2026-08-08 实测）

正文是 **Canvas 渲染**，DOM 无文本。**可行路径 = 从页面内存对象读文本池**：

```
window.pad.editor._state._dataEngine.dataManager.dataStream.textPool
  ._size                    → 文档总字符数（含格式标记，先看这个确认规模）
  ._textBuffer._poolPages   → 约 36 个 page 对象数组，每个是 {索引: 字符码}
```
解码：遍历所有 page，`String.fromCharCode(code)` 还原；第 0 页开头有 `\u0000` 控制符，正文从实际内容起；长文档（10KB+）分段取页，别一次全量 JSON.stringify。

大纲：`browser_snapshot` 无障碍树侧栏"大纲"面板直接可见全部章节标题（这一步通常成功，正文才是难点）。

### 已排除路径（别浪费时间）
- `window.openDocResponseText` — 只有元数据（title/权限），无正文
- `window.pad.collab.changesetManager` — 协作增量，无完整文本
- `#melo-hidden-editor`（contenteditable）— 始终为空；点击聚焦 + `Ctrl+~` 无障碍模式都不填充
- `navigator.clipboard.readText()` — `Read permission denied`
- `curl .../dop-api/opendoc` 或 `.../doc/export` — 需登录态（404/403/blankpage）

### 配套
- 提取出的文本含 `\u0000` 等格式标记，整理时过滤
- 提取后若要整理成教程/skill，接 technical-tutorial-authoring 主流程（Step 2-6）
- 适用于 padType=doc 的腾讯文档；表格/幻灯片类未验证

## 通用思路（其他 Canvas 渲染文档）

1. 先试无障碍树/aria：`document.querySelector('[role="textbox"]')` 等，多数情况为空
2. 找页面全局对象：`Object.keys(window).filter(k => /doc|state|data|init|pad/i.test(k))`
3. 逐层深入编辑器实例：`pad.editor._state._dataEngine.dataManager.dataStream.*` 这类路径
4. 找 `textPool / textStream / dataStream` 之类名字——正文往往以字符码/池的形式存在
5. 剪贴板读取（execCommand('copy') + navigator.clipboard）在浏览器工具里权限受限，基本不可用

## 参考

- 详细逐层探索记录：`references/tencent-docs-extraction.md`
