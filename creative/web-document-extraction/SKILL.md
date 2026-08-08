---
name: web-document-extraction
description: "从受限网页/文档提取全文：腾讯文档（docs.qq.com）Canvas textPool 解码、Blob 下载、清洗、结构化配方解析。适用于任何 Canvas 渲染无法直接 DOM 读取的文档（魔法书、教程、规范）。8+ 次实测成功（元素法典/解构原典系列）。"
version: 1.0.0
author: agent
tags: [tencent-docs, docs.qq.com, web-extraction, canvas, textpool, 腾讯文档, 文档提取]
platforms: [windows, macos, linux]
---

# Web 文档提取（腾讯文档 Canvas 解码法）

从 **Canvas 渲染**的受限网页文档中提取全文。腾讯文档正文用 Canvas 绘制，`document.body.innerText` 只有标题/批注/大纲，DOM 拿不到正文；`#melo-hidden-editor`（无障碍 textbox）一直为空。本技能记录实测 8+ 次成功的提取路径（《元素法典》×4 + 《解构原典》×4，2026-08）。

## 触发条件

- 用户给 docs.qq.com 链接要求研究/学习/整理
- 需要从 Canvas 渲染的网页提取正文（教程、魔法书、规范文档）
- 需要把腾讯文档内容转成 skill / 配方库 / 结构化文件

## 关键：textPool 数据引擎

页面加载完成后（`window.pad` 出现，等 5-10s），正文文本池在：

```
window.pad.editor._state._dataEngine.dataManager.dataStream.textPool
```

- `textPool._textBuffer._poolPages` = **36 页 × 2048 槽位**的字符码数组（`{槽位: Unicode 码点}`）
- `textPool._size` ≈ 文档字符数（含格式标记）
- 每页的 key 是**页内偏移**（0-2047），不是全局索引——**必须按页拼接**

### 解码（浏览器 console，一次性提取全文）

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
      if (typeof code === 'number' && code > 0) pageChars[k] = String.fromCharCode(code);
    }
    chunks.push(pageChars.join(''));
  }
  const text = chunks.join('');
  window.__docText = text;   // 挂到 window 供后续读取
  return 'length=' + text.length;
})()
```

⚠️ 常见 bug：只解码 `_poolPages[0]` 或把每页 key 当全局索引 → 只拿到最后一页（length≈2048）。**必须逐页拼接**。

## 保存到本地：Blob 下载（推荐）

浏览器 console 里用 Blob 触发下载（HTTPS 页面 fetch 本地 HTTP 服务器会被混合内容拦截，别走 POST 本地服务那条路）：

```js
(() => {
  const blob = new Blob([window.__docText], {type: 'text/plain;charset=utf-8'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'doc_raw.txt';
  document.body.appendChild(a); a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  return 'download triggered';
})()
```

文件落到 `C:/Users/<user>/Downloads/`（UTF-8 带 BOM）。

## 清洗（Python）

```python
import re
text = text.lstrip('\ufeff')
text = re.sub(r'\u0013HYPERLINK.*?\u0015', '', text, flags=re.DOTALL)  # 去链接标记块
text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\u0005\u0013\u0014\u0015]', '', text)  # 去控制字符
text = text.replace('\b', '')  # \b 是图片占位符
text = re.sub(r'[ \t]+\r\n', '\r\n', text)
text = re.sub(r'\r\n{3,}', '\r\n\r\n', text)  # 压缩空行
```

⚠️ 脚本里的 `\x` 转义**必须写进 .py 文件执行**，直接 heredoc `python - <<'EOF'` 会被 bash 吃反斜杠 → `re.PatternError: unterminated character set`。

## 结构识别（魔法书/配方文档）

- 文本配方区通常在**文末**（「Presentjiantous by …」之后）——正文区魔法目录的 tag 常以**图片**存在（\b 占位符），只有文末区是完整文本配方
- 魔法标题定位：文档大纲（body.innerText）能拿到所有标题名，在清洗文本里按行匹配标题行，标题间即该魔法正文
- 配方格式：正向 tag 行 → 负向行 → 参数行（Steps/Sampler/CFG/Size/Seed/Clip skip/ENSD），解析按「参数行切分」+「跨行 prompt 合并」

## 已探明的坑

- `openDocResponseText` / `bodyData` 只有元数据没有正文
- `pad.collab.changesetManager` 等深层对象太绕，别走
- 页面刷新会丢 `window.pad`——重新 navigate 后等 5-10s 再取
- 腾讯文档导出 API（`/dop-api/export/...`）未登录态 404/403，别指望
- 权限允许复制（`view_forbid_copy_print: 0`）但 `navigator.clipboard.readText()` 被浏览器权限拦，走 Blob 下载最稳
- 大文档（>90K 字符）分块提取时用 `window.__docText` 存全文再统一下载，避免 console 输出截断

## 下游：配方整理成 skill

提取清洗后的文档可沉淀为提示词魔法书 skill（本技能的应用案例）：
- `sd-prompt-methodology` — 提示词方法论（权重语法/词序公式）
- `novelai-element-codex` — NAI1 时代配方库（references/recipes*.json）
- `nai3-deconstruction-codex` — NAI3 时代配方库（references/v*-recipes.md）

下游整理流程：提取 → 清洗 → 通读定位结构 → 提取配方 JSON → 精选写入 SKILL.md + references → 校验 skill 加载。SKILL.md 超 100K 时配方放 references、正文只留索引表。

## 参考链接

- 腾讯文档正文解码路径来自实测（docs.qq.com 编辑器内核 melo）
- 与 `technical-tutorial-authoring`（受保护技能，含飞书/语雀受限文档技巧）互补
