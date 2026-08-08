---
name: tencent-docs-extraction
description: "从腾讯文档（docs.qq.com）提取 Canvas 渲染的正文全文：textPool 解码法。公开只读文档无需登录即可拿到 3万~9万字符完整文本（已验证 7 次：元素法典 4 卷 + 解构原典 4 卷）。含 Blob 下载、Python 清洗、魔法书类文档结构识别。"
version: 1.0.0
author: agent
tags: [tencent-docs, docs.qq.com, canvas-extraction, web-scraping, 腾讯文档, textpool, browser]
platforms: [windows, macos, linux]
---

# 腾讯文档正文提取（textPool 解码法）

腾讯文档（docs.qq.com）正文用 Canvas 渲染，DOM 里没有文本（`body.innerText` 只有标题/大纲/批注）。本技能提供**已验证 7 次**的完整提取流程：元素法典 4 卷 + 解构原典 4 卷，均成功提取 3万~9万字符全文。

## 触发条件

- 链接形如 `https://docs.qq.com/doc/XXXX` 的公开只读文档
- `browser_snapshot` 只看到大纲/工具栏，正文 Canvas 无文本
- 用户说「研究/整理/保存」某个腾讯文档链接

## 步骤

### 1. 打开并等待渲染
```python
browser_navigate("https://docs.qq.com/doc/DWHl3am5Zb05QbGVs")
```
等 ~8s（Canvas 渲染 + websocket 加载 chunk）。确认就绪：console 执行 `typeof window.pad` → `"object"`（编辑器对象异步初始化，sleep 8s 后再查）。

### 2. 解码 textPool（核心）
浏览器 console 执行（一次性取全文，存 `window.__docText`）：
```js
(() => {
  const buf = window.pad.editor._state._dataEngine.dataManager.dataStream.textPool._textBuffer;
  const pages = buf._poolPages;               // 页面数组，每页 2048 字符槽
  const chunks = [];
  for (let i = 0; i < pages.length; i++) {
    const p = pages[i];
    if (!p || typeof p !== 'object') { chunks.push(''); continue; }
    const keys = Object.keys(p).map(Number).sort((a,b) => a-b);  // 页内偏移
    const pageChars = [];
    for (const k of keys) { const code = p[k]; if (typeof code === 'number' && code > 0) pageChars[k] = String.fromCharCode(code); }
    chunks.push(pageChars.join(''));
  }
  const text = chunks.join('');
  window.__docText = text;
  return 'length=' + text.length + '\nHEAD:\n' + text.slice(0, 900);
})()
```

**关键坑**：`_poolPages` 每页 key 是**页内偏移**（0-2047），不是全局索引。必须逐页拼接——如果按全局索引填数组会只剩最后一页内容。`textPool._size`（如 73567）≈ 总字符数，用于 sanity check。

### 3. 保存到本地（Blob 下载）
**不要**用 fetch POST 到本地 HTTP 服务——https 页面请求 http://127.0.0.1 被混合内容策略拦截（`Failed to fetch`）。用 Blob 触发下载：
```js
(() => {
  const text = window.__docText;
  const blob = new Blob([text], {type: 'text/plain;charset=utf-8'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'doc_raw.txt';
  document.body.appendChild(a); a.click();
  document.body.removeChild(a); URL.revokeObjectURL(url);
  return 'download triggered, size=' + text.length;
})()
```
文件落在 `C:\Users\<user>\Downloads\`（Chromium 默认下载目录），然后 `cp` 到工作目录。

### 4. Python 清洗
用 `write_file` 写清洗脚本（**不要**用 bash heredoc 写含 `\x` 转义的 Python——shell 吃反斜杠导致 `re.PatternError: unterminated character set`）。规则：
```python
text = text.lstrip('\ufeff')
text = re.sub(r'\u0013HYPERLINK.*?\u0015', '', text, flags=re.DOTALL)   # 链接标记
text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\u0005\u0013\u0014\u0015]', '', text)  # 控制符
text = text.replace('\b', '')                                            # 图片占位
text = re.sub(r'[ \t]+\r\n', '\r\n', text)
text = re.sub(r'\r\n{3,}', '\r\n\r\n', text)
```

## 文档结构识别（魔法书/配方类文档）

- **文末文本配方区**：从 `Presents by` / `Presentjiantous` 行到「投稿基础要求」/「本书本着开源」前——**完整可提取的配方**。参数行特征：`steps:28 / height:1216 / CFG scale / sampler:"k_euler"` 等
- **目录区**：魔法标题+作者+编者注，但 tag 是**图片**（`\b` 占位），无法提取文本——保留名称+作者索引，明确告知用户「tag 为图片不可提取，可截图补录」
- 配方解析：正向行（长逗号句+质量词）→ 负向行（nsfw/lowres/worst quality 开头）→ 参数行（steps/scale/seed/sampler）一组；参数行结束=配方切分点。跨行 prompt 要合并；说明性中文行（「本法」「要点」「可以加入」）要过滤

## 注意

- 页面可能中途刷新导致 `window.pad` 丢失——重新 `browser_navigate` 后等 8s 再解码
- `browser_console` 里 `() => {}` 箭头函数偶尔报 `Unexpected end of input`——改用 `(() => {...})()` 自执行
- 大文档（9万字符）console 返回值有截断，解码后先 `return 'length=' + len` 确认，再触发下载
- 配合 `sd-prompt-methodology` / `novelai-element-codex` / `nai3-deconstruction-codex` 使用（提取结果整理成提示词配方 skill）
