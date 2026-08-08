---
name: canvas-doc-extraction
description: "从 Canvas 渲染的在线文档提取全文（腾讯文档 docs.qq.com 等）：绕过 DOM 空文本，直接解码页面 JS 内核的 textPool（_poolPages 字符码数组），用 Blob 下载保存。2026-08 实测成功提取 8+ 篇《元素法典》/《解构原典》系列（每篇 3万-9万字符）。"
version: 1.0.0
author: agent
tags: [tencent-docs, docs.qq.com, canvas, text-extraction, web-scraping, 腾讯文档, 提取文本]
platforms: [windows, macos, linux]
---

# Canvas 文档全文提取（textPool 法）

腾讯文档（docs.qq.com）等用 Canvas 渲染正文，DOM / 无障碍树（`#melo-hidden-editor`）都拿不到文本。但页面 JS 内核持有完整文本池，可直接解码。**适用场景**：需要把在线文档全文保存/清洗/入库（技能整理、知识库构建、批量抓取文档系列）。

## 触发条件

- 需要读取腾讯文档（docs.qq.com/doc/...）的完整正文
- 文档正文在 Canvas 里、`browser_snapshot` 只拿到大纲/批注、`#melo-hidden-editor` 为空
- 需要批量提取一系列同源文档（如某法典/教程的多个分卷）

## 提取流程

### 1. 打开文档并等 JS 内核就绪
`browser_navigate` 打开链接后 `sleep 8`，探测 `typeof window.pad` 应为 `"object"`（页面 JS 内核）。

### 2. 解码 textPool（核心步骤）
textBuffer 的 `_poolPages` 是页面数组（每页 2048 槽位存 UTF-16 字符码）。**关键：按页内索引填槽，不是全局索引**——否则各页互相覆盖只剩最后一页。

```js
(() => {
  const buf = window.pad.editor._state._dataEngine.dataManager.dataStream.textPool._textBuffer;
  const pages = buf._poolPages;
  const chunks = [];
  for (let i = 0; i < pages.length; i++) {
    const p = pages[i];
    if (!p || typeof p !== 'object') { chunks.push(''); continue; }
    const keys = Object.keys(p).map(Number).sort((a,b) => a-b);
    const pageChars = [];
    for (const k of keys) {
      const code = p[k];
      if (typeof code === 'number' && code > 0) { pageChars[k] = String.fromCharCode(code); }
    }
    chunks.push(pageChars.join(''));
  }
  window.__docText = chunks.join('');
  return 'length=' + window.__docText.length + '\nHEAD:\n' + window.__docText.slice(0, 800);
})()
```

**定位路径速记**：`window.pad` → `editor` → `_state` → `_dataEngine` → `dataManager` → `dataStream` → `textPool` → `_textBuffer` → `_poolPages`。

### 3. 保存全文（Blob 下载）
⚠️ https 页面 fetch 不到 `http://127.0.0.1`（混合内容被浏览器拦截），别起本地 HTTP 服务器接收。用 Blob 下载触发，文件落到浏览器下载目录（Windows 默认 `C:/Users/<user>/Downloads/`）：

```js
(() => { const t = window.__docText;
  const blob = new Blob([t], {type:'text/plain;charset=utf-8'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href = url; a.download = 'doc_raw.txt';
  document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url);
  return 'download triggered, size=' + t.length; })()
```

### 4. 清洗（去控制字符 + HYPERLINK 标记）
```python
text = text.lstrip('\ufeff')
text = re.sub(r'\u0013HYPERLINK.*?\u0015', '', text, flags=re.DOTALL)
text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\u0005\u0013\u0014\u0015]', '', text)
text = text.replace('\b', '')
text = re.sub(r'\r\n{3,}', '\r\n\r\n', text)
```

⚠️ **用 write_file 写 Python 脚本再执行**——heredoc 里 `\x` 转义会被 shell 吃掉，导致 `unterminated character set` regex 报错（实测踩过两次）。

## 结构化提取技巧（文档系列场景）

对「魔法配方/教程条目」类文档，清洗后可进一步：
- 用正则/脚本按条目标题切段（如 `re.findall` 找 `XX法` 标题行）
- 每个条目的 正面tag/负面tag/参数 分字段提取为 JSON
- 存档：`E:\ai1\comfyui_workflow\` 下保留 `*_raw.txt` + `*_clean.md` + `*_recipes.json`

## 已知限制

- 页面刷新后 `window.pad` 丢失 → 需重新 navigate + 等待
- 文档内嵌图片以 `\x08`/`\b` 占位（图片内容无法提取文本，如法典里的配方图）
- 未登录只读模式可读文本池；`advPolicy.view_forbid_copy_print` 通常为 0（允许查看）
- 其他兜底（均不如 textPool 有效）：`window.openDocResponseText.bodyData` 只有元数据；`pad.editor` 深层对象无现成 getText 方法；Ctrl+~ 无障碍模式在现行版本无效

## 参考链接

- 本技能实战产出：`novelai-element-codex`（元素法典 4 卷）与 `nai3-deconstruction-codex`（解构原典 4 卷）两个 skill 的全部配方均由此法提取
- 网页提取通用流程：见 `technical-tutorial-authoring` skill
