# 腾讯文档 (docs.qq.com) 正文提取——完整探索记录（2026-08-08 实测）

## 场景

用户给了 B 站专栏姊妹篇《元素法典》的腾讯文档链接（docs.qq.com/doc/DWHl3am5Zb05QbGVs），要求"研究学习"。文档 69 页/10448 字/文本池 73728 字符。未登录只读模式。

## 成功路径

1. `browser_navigate` 打开文档，`browser_snapshot` 拿到**大纲**（无障碍树侧栏，58+ 章节标题齐全）
2. 正文 DOM 提取全空——腾讯文档正文 Canvas 渲染，`#melo-hidden-editor` contenteditable 始终 0 字符
3. 找到关键对象：`Object.keys(window)` 里出现 `pad`、`openDocResponseText` 等
4. 逐层深入最终定位文本池：
   ```
   window.pad.editor._state._dataEngine.dataManager.dataStream.textPool
   ```
   - `textPool._size` = 73728（总字符数，含格式标记）
   - `textPool._textBuffer._poolPages` = 36 个 page 对象数组
   - 每个 page：`{0: 80, 1: 114, 2: 101, ...}` = 字符码映射（80='P', 114='r', 101='e', 115='s' → "Pres..."）
   - 开头有 `\u0000` 控制符，正文从实际内容起

5. 解码方法：
   ```js
   const buf = window.pad.editor._state._dataEngine.dataManager.dataStream.textPool._textBuffer;
   let text = '';
   for (const page of buf._poolPages) {
     for (const k of Object.keys(page)) text += String.fromCharCode(page[k]);
   }
   ```
   ⚠️ 长文档别一次 JSON.stringify 全量（超出 console 返回限制），先 `_size` 确认规模，再分段取。

## 逐层探索路径（记录用，变体文档可复用）

```
window.pad                          → 编辑器容器（renderFinish=true 表示渲染完成）
  .editor                           → 编辑器实例
  .editor._state._dataEngine        → 数据引擎
  ._dataEngine.dataManager.dataStream → 数据流
  .dataStream.textPool              → 文本池（textPool._size 总长度）
  .textPool._textBuffer._poolPages  → 字符码页数组 ✅
```

旁路对象（都试过，正文不在这）：
- `window.openDocResponseText` — 只有元数据（title/privilege/advPolicy/collab_client_vars），正文不在
- `window.pad.collab.changesetManager` — 协作增量，无完整文本
- `window.pad.controllerCenter.plugins` — 空
- `window.documentManager` — 只有 isContainerReady

## 已排除的死路

| 尝试 | 结果 |
|------|------|
| `document.getElementById('melo-hidden-editor').innerText` | 始终 0（点击聚焦、Ctrl+~ 无障碍、execCommand('selectAll') 都没用） |
| `navigator.clipboard.readText()` | `Read permission denied`（浏览器工具读不到剪贴板） |
| `curl docs.qq.com/dop-api/opendoc?id=...` | 需登录态，返回 blankpage/oidbret |
| `curl docs.qq.com/doc/export?docId=...` | 404（需登录态） |
| 页面 iframe | 0 个 iframe，2 个 canvas——别找 iframe |

## 观察

- `advPolicy.view_forbid_copy_print: 0` = 允许复制打印，但 DOM 层仍拿不到，只能走内存对象
- 页面提示"用户可以通过 control 加 ~ 打开或关闭无障碍功能"——实测 Ctrl+~ 不填充正文元素
- 该方法适用于 padType=doc 的腾讯文档；表格/幻灯片/文件夹类未验证

## 后续处理

提取出原始文本后（含 \u0000 等格式标记需过滤），若用户要"整理成 skill/教程"：
- 接 `technical-tutorial-authoring` 主流程（Step 2-6：整理→补充→结构化 MD）
- 本次产出：`sd-prompt-methodology` skill（提示词方法论，含权重语法/元素分类/词序公式，来源 B站 cv19505389 + 腾讯文档《元素法典》目录框架）
