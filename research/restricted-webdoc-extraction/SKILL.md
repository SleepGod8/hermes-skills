---
name: restricted-webdoc-extraction
description: "受限在线文档全文提取：腾讯文档（docs.qq.com）Canvas 渲染正文的 textPool 内部结构解码法（8 次实测 100% 成功）；飞书/语雀登录遮罩、Notion 等受限页面的浏览器提取路径。产出可清洗的原始文本供整理成 MD/教程/skill。"
version: 1.0.0
author: agent
tags: [document-extraction, tencent-docs, docs.qq.com, textpool, web-scraping, canvas-rendered, 腾讯文档, 文档提取]
platforms: [windows, macos, linux]
---

# 受限在线文档全文提取（Restricted Web Document Extraction）

当用户分享**在线文档链接**（腾讯文档 / 飞书 / 语雀 / Notion / 金山文档）并要求读取/研究/整理内容时使用。核心难点：这类文档要么 Canvas 渲染（DOM 无文本），要么登录遮罩。本技能记录已验证的提取路径。

## 触发条件

- 用户给出 docs.qq.com / feishu / yuque / notion 等受限文档链接，要求读取或研究内容
- 页面能打开但正文提取不到（`body.innerText` 只有标题/大纲/批注）
- 需要把在线文档内容整理成 skill / MD 教程 / 知识库

## 腾讯文档（docs.qq.com）：textPool 解码法（8 次实测 100%）

### 为什么 DOM 提取不行

正文在 **Canvas 渲染**：
- `document.querySelector('[role="textbox"]').textContent` → 空
- `body.innerText` → 只有标题/大纲/评论区
- 无障碍模式（Ctrl+~）无效，`#melo-hidden-editor` 恒为空
- curl 导出接口（`/dop-api/export/docx` 等）需登录态，返回 404/403

### 核心原理

文档正文以 **UTF-16 字符码**存在 textPool 的页式缓冲区，可从浏览器 JS 直接读出：

```
window.pad.editor._state._dataEngine.dataManager.dataStream.textPool
  └─ _textBuffer._poolPages[]   // 每页 2048 槽位
```

### 提取步骤

1. **导航并等待**：`browser_navigate(url)` → `sleep 8` → `typeof window.pad === 'object'`
2. **确认就绪**：
   ```js
   (() => { try { const ds = window.pad.editor._state._dataEngine.dataManager.dataStream;
     const pages = ds.textPool._textBuffer._poolPages; let t=0;
     for (let i=0;i<pages.length;i++){const p=pages[i]; if(p&&typeof p==='object') t+=Object.keys(p).length;}
     return 'ready, chars='+t; } catch(e){ return 'not ready: '+e.message; } })()
   ```
3. **解码全文**（关键：每页 key 是**页内偏移**，按页拼接，不能当全局索引）：
   ```js
   (() => { const buf = window.pad.editor._state._dataEngine.dataManager.dataStream.textPool._textBuffer;
     const pages = buf._poolPages; const chunks = [];
     for (let i = 0; i < pages.length; i++) {
       const p = pages[i];
       if (!p || typeof p !== 'object') { chunks.push(''); continue; }
       const keys = Object.keys(p).map(Number).sort((a,b) => a-b);
       const pageChars = [];
       for (const k of keys) { const code = p[k];
         if (typeof code === 'number' && code > 0) pageChars[k] = String.fromCharCode(code); }
       chunks.push(pageChars.join(''));
     }
     const text = chunks.join(''); window.__docText = text;
     return 'length=' + text.length + '\nHEAD:\n' + text.slice(0, 900); })()
   ```
4. **Blob 下载到本地**（https 页面 fetch http://127.0.0.1 会被混合内容拦截）：
   ```js
   (() => { const text = window.__docText;
     const blob = new Blob([text], {type:'text/plain;charset=utf-8'});
     const url = URL.createObjectURL(blob); const a = document.createElement('a');
     a.href = url; a.download = 'doc.txt'; document.body.appendChild(a); a.click();
     document.body.removeChild(a); URL.revokeObjectURL(url);
     return 'download triggered, size=' + text.length; })()
   ```
   文件落在 `C:\Users\<user>\Downloads\`，复制到工作目录后清洗。

5. **清洗**（⚠️ heredoc 写 Python 正则会被 shell 转义吃字符，必须 write_file 脚本再执行）：
   ```python
   text = text.lstrip('\ufeff')
   text = re.sub(r'\u0013HYPERLINK.*?\u0015', '', text, flags=re.DOTALL)  # 链接块
   text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\u0005\u0013\u0014\u0015]', '', text)  # 控制字符
   text = text.replace('\b', '')  # 图片占位符
   text = re.sub(r'\r\n{3,}', '\r\n\r\n', text)  # 压缩空行
   ```

### 已踩的坑

| 坑 | 现象 | 解法 |
|---|---|---|
| 页面刷新丢状态 | `window.pad` 变 undefined | 重新 navigate + 等 8 秒 |
| 解码索引错 | 只有最后一页内容 | 每页独立 `pageChars[k]` 再 join（key 是页内偏移） |
| console 返回超长 | 截断/EOF | 用 Blob 下载，不要直接 return 全文 |
| 正文边界 | 开头是封面/前言，文末常附配方区 | 按「前言/相关链接/目录」标记定位 |
| 批注混排 | 文首出现评论区文字 | 清洗时识别并跳过 |
| 部分魔法/条目 tag 是图片 | `\b` 占位符，提取不到 | 只保留名称+作者索引，标注"tag 为图片不可提取" |

### 文档结构规律（法典/配方类长文档）

- **文末常附完整文本配方区**（如「Presentjiantous by ...」之后），比目录区（tag 是图片）有价值得多
- 目录区魔法条目通常只有标题+作者+编者注，tag 是图片 → 只做名称索引
- 提取后按空行/标记切分，可批量转为 JSON 配方库（`references/` 下的 `recipes_*.json`）

## 飞书 / 语雀 / Notion

- 登录遮罩下的提取思路与坑见 `technical-tutorial-authoring` 技能的 `references/feishu-login-techniques.md`、`references/hermes-studio-browser-reading.md`
- 不要替用户登录第三方网站
- 未登录能读到目录/标题/关键语句就用，图片遮挡用自身知识补充并标注

## 验证

- [ ] 解码长度合理（几万字=长文档，几百字=可能没就绪）
- [ ] 头部含文档标题/封面，确认是正文而非 UI 文案
- [ ] 清洗后无 `\u0013`/`\b`/HYPERLINK 残留
- [ ] 提取内容与页面大纲标题对得上
