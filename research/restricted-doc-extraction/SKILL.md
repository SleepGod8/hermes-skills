---
name: restricted-doc-extraction
description: "提取受限/Canvas 渲染网页文档的完整正文（腾讯文档 textPool 解码、Blob 下载、清洗、结构化提取）。正文在 Canvas 里、DOM 读不到的文档用此法。2026-08 实测成功提取《元素法典》四卷+《解构原典》四卷。与 technical-tutorial-authoring 互补（那个是被保护技能，只覆盖飞书/语雀）。"
version: 1.0.0
author: agent
tags: [web-extraction, tencent-docs, docs-qq-com, canvas, textpool, scraping, 文档提取]
platforms: [windows, macos, linux]
---

# 受限文档正文提取（Canvas 渲染 / JS 生成内容）

当网页文档正文在 Canvas 里渲染（DOM 读不到文本、body.innerText 只有大纲/批注/工具栏）时，用本技能。2026-08 实测：腾讯文档（docs.qq.com）8 卷长文档全部成功提取（30K-90K 字符/卷）。

## 触发条件

- 腾讯文档链接（docs.qq.com/doc/...），需要完整正文
- 任何"正文在 Canvas 里"的文档：`document.body.innerText` 拿不到正文
- `browser_snapshot` 只见大纲/批注/标题，正文区为空
- 需要从在线文档批量提取结构化配方/条目（如提示词配方、教程正文）

## 判断是否可用 textPool 法

```js
typeof window.pad  // object = 编辑器已就绪
```
就绪后查正文池大小（约 73728 满池/36 页）：
```js
(() => { const ds = window.pad.editor._state._dataEngine.dataManager.dataStream;
  const tp = ds.textPool, buf = tp._textBuffer, pages = buf._poolPages;
  let total = 0; for (let i = 0; i < pages.length; i++) { const p = pages[i];
    if (p && typeof p === 'object') total += Object.keys(p).length; }
  return 'chars=' + total; })()
```

## 核心解码（textPool → 全文）

`window.pad.editor._state._dataEngine.dataManager.dataStream.textPool._textBuffer._poolPages`
= 36 个页面数组，每页 `{offset: charCode}`（UTF-16 码点）。

**⚠️ 每页 key 是页内偏移，必须按页拼接**。全局索引 `chars[Number(k)]` 会互相覆盖，只剩最后一页内容：
```js
(() => { const buf = window.pad.editor._state._dataEngine.dataManager.dataStream.textPool._textBuffer;
  const pages = buf._poolPages, chunks = [];
  for (let i = 0; i < pages.length; i++) { const p = pages[i];
    if (!p || typeof p !== 'object') { chunks.push(''); continue; }
    const keys = Object.keys(p).map(Number).sort((a,b) => a-b), pageChars = [];
    for (const k of keys) { const code = p[k];
      if (typeof code === 'number' && code > 0) pageChars[k] = String.fromCharCode(code); }
    chunks.push(pageChars.join('')); }
  const text = chunks.join(''); window.__docText = text;
  return 'length=' + text.length; })()
```

## 保存到本地：Blob 下载（不要 fetch 本地服务器）

HTTPS 页面 fetch `http://127.0.0.1` 会被**混合内容拦截**（"Failed to fetch"）；`navigator.clipboard.readText()` 权限被拒。正确做法是**触发浏览器下载**（落在 `~/Downloads/`）：
```js
(() => { const text = window.__docText;
  const blob = new Blob([text], {type: 'text/plain;charset=utf-8'});
  const url = URL.createObjectURL(blob); const a = document.createElement('a');
  a.href = url; a.download = 'doc_raw.txt'; document.body.appendChild(a);
  a.click(); document.body.removeChild(a); URL.revokeObjectURL(url);
  return 'size=' + text.length; })()
```
然后 `ls ~/Downloads/doc_raw.txt` → 复制到工作目录。

## 清洗

用 `write_file` 写 Python 脚本再执行——**heredoc 里 `\x`/`\u` 会被 shell 吞，re 报 unterminated character set**：
```python
import re
text = open(RAW, encoding='utf-8').read()
text = text.lstrip('\ufeff')
text = re.sub(r'\u0013HYPERLINK.*?\u0015', '', text, flags=re.DOTALL)  # 超链接标记块
text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\u0005\u0013\u0014\u0015]', '', text)
text = text.replace('\b', '')  # 图片占位符
text = re.sub(r'[ \t]+\r\n', '\r\n', text)
text = re.sub(r'\r\n{3,}', '\r\n\r\n', text)
```

## 结构化提取（配方/条目模式）

腾讯文档 textPool 顺序≠视觉顺序：批注/评论会混入正文区。常见结构：文末文本配方区（三行一组：正向/负向/参数）+ 目录区（tag 以图片存在，`\b` 占位 → 只能留名称索引）。

分类正则（可复用）：
```python
def is_param_line(s):     # 参数行：steps/cfg/scale/sampler/size/seed/clip skip/ensd...
def is_negative_line(s):  # 负向：含 lowres/bad anatomy/nsfw/watermark + 逗号
def is_prompt_line(s):    # 正向：>25 字符 + (逗号|花括号|masterpiece|quality|1girl)
# 遇参数行切分配方；跨行正向累加
```

## 坑汇总

1. **每页 key 是页内偏移**——按页拼接，别全局索引
2. **`\x08` 是图片占位符**——tag 以图片存在的条目无法从文本提取，留名称索引并告知用户可截图补录
3. **清洗脚本用 write_file 写**，heredoc 会被 shell 吃转义
4. **HTTPS 页面不能 fetch 本地 HTTP 服务器**——用 Blob 下载
5. **页面刷新后 window.pad 丢失**——重新 navigate，sleep 8s 再解
6. **Ctrl+~ 无障碍模式在当前版本无效**；`initialAttributedText.text` 初始为空——别在这两条路上绕
7. 前端 fetch 自身 API（如 `/userdata/workflows/...`）可能 404/空——外部文件直接 Blob 下载最稳

## 参考

- 完整实战（八卷提取 + 配方整理）：见 `novelai-element-codex` / `nai3-deconstruction-codex` skills
- 文档内容加工为教程：`technical-tutorial-authoring`（受保护，无法修改，但流程可参考）
