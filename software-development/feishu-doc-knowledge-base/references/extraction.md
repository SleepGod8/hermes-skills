# 飞书文档提取详细配方（references/extraction.md）

实战来源：知识库「AI项目603」（分享者 Jeremy_wl，密码 Wolin0603），42 篇 / 23k 块 / 81 万字符全量抓取。

## 1. 密码解锁（wiki 首页）

```js
// browser_navigate 到 wiki URL 后，若 snapshot 出现「请输入密码访问」
// 输入框 ref 如 @e10，确定按钮如 @e5（disabled，输入后启用）
browser_type(ref='@e10', text='<密码>')
browser_click(ref='@e5')
```
- 密码 cookie 对同空间子文档有效；**回知识库首页需重新输入**（会话可能重置）
- 子文档（`/wiki/<token>`）直接访问通常无需密码

## 2. 完整目录树（递归）

第 1 步，在**根页面**（非子文档页）执行：
```js
(async () => {
  const r = await fetch('/space/api/wiki/v2/tree/get_info/?space_id=7551707996851519516&with_space=true&with_perm=true&expand_shortcut=true&need_shared=true&exclude_fields=5&with_deleted=true&wiki_token=W3utwEYq8i605ikYyzQcYqdOnOf', { credentials: 'include' });
  const j = await r.json();
  return JSON.stringify(j.data.tree);
})()
```
- `child_map[父token]` → 子 token 数组；`nodes[token]` → {title, obj_token, obj_type(22=docx), url, has_child}
- 递归：对每个 has_child 节点再调 get_info（wiki_token=该节点），直到无子节点
- 根节点 wiki_token = 分享链接里的 `/wiki/<token>` 段
- **坑**：在子文档页调用 get_info 会返回空 child_map；务必先导航回根页

## 3. 正文 DOM 收集（虚拟列表）

关键事实：docx 正文走 websocket（pandora_ws），REST 拿不到；DOM 是虚拟列表（只渲染视口附近，滚动回收旧节点）。

滚动容器：`.bear-web-x-container`（`scrollHeight` 可达数万 px，clientHeight ~550px）。

标准收集脚本（browser_console 执行，存 window 防截断）：
```js
(async () => {
  await new Promise(r => setTimeout(r, 2000));
  const scroller = document.querySelector('.bear-web-x-container') || document.scrollingElement;
  if (!scroller) return JSON.stringify({ n: 0, reason: 'no-scroller' });
  scroller.scrollTop = 0;
  window.__blocks = [];
  const seen = new Set();
  const collect = () => {
    document.querySelectorAll('[data-block-id]').forEach(el => {
      const cls = (el.className || '').toString();
      if (/docx-page-block|docx-view-block|docx-file-block/.test(cls)) return;
      const t = (el.textContent || '').replace(/\u200b/g, '').replace(/\u200e/g, '').trim();
      if (!t) return;
      if (seen.has(t)) return;
      seen.add(t);
      let c = 't';
      if (cls.includes('heading2')) c = 'h2';
      else if (cls.includes('heading3')) c = 'h3';
      else if (cls.includes('heading4')) c = 'h4';
      else if (cls.includes('bullet')) c = 'b';
      else if (cls.includes('code')) c = 'c';
      window.__blocks.push([c, t]);
    });
  };
  await new Promise(r => setTimeout(r, 500));
  collect();
  let lastY = -1, guard = 0;
  while (guard < 60) {
    guard++;
    scroller.scrollTop += scroller.clientHeight * 0.8;
    await new Promise(r => setTimeout(r, 180));
    collect();
    if (scroller.scrollTop === lastY) break;
    lastY = scroller.scrollTop;
  }
  const chars = window.__blocks.reduce((a, b) => a + b[1].length, 0);
  return JSON.stringify({ n: window.__blocks.length, chars, tooBig: chars > 24000 });
})()
```
- `tooBig=true` → 分段取回，每段 280 块：
  `(() => JSON.stringify(window.__blocks.slice(0,280)))()`、`slice(280,560)`…直到取完
- **尾部兜底**：guard 到 60 可能漏尾部（虚拟列表没渲染完）；改进版把 guard 提到 150，最后 `scroller.scrollTop = scroller.scrollHeight` 等 500ms 再 collect 一次
- 子 agent 分段抓取后必须核对 part 数/块数，缺尾的要重抓（本次 5MVP 缺 part4、WL 只有 600/901 块都是这么发现的）

## 4. docx 直链绕过登录墙

现象：`/wiki/<token>` 302 到 `accounts.feishu.cn` 扫码登录页（文档是独立分享/组织内可见，密码解不了）。
解法：`https://<tenant>.feishu.cn/docx/<obj_token>` 直链 → 302 回 wiki 页但直接显示内容。
obj_token 从目录树 nodes 拿（不是 wiki_token！两者不同）。

## 5. 子 agent 并行

- 3 个并行子 agent，每个 5-8 篇；浏览器会话/cookie 共享（密码主会话解锁一次即可）
- context 必须含：密码、标准收集脚本（含 tooBig 分段规则）、落盘路径 `feishu_import/raw/<标题>.json`、空文档规则（n=0 存 []）、返回格式（状态摘要）
- 完成后核对：part 文件是否合并、是否被登录重定向中断、是否改了共享脚本

## 6. 清洗要点

- 去零宽：`\u200b\u200e\ufeff`；`\u00a0`→空格
- 代码块提取：`代码块XXX复制<真实代码>` → 正则 `代码块\s*(.*?)复制\s*(.*)$`
- 语言映射：python→python、java/go→bash、markdown→yaml、xml→xml、plain text→''
- 图片块（image-）文本为空，跳过（原始文档中的图片丢失，可接受）
- 表格在 textContent 里是连排文本（列值黏连），保留原样
