---
name: feishu-doc-extraction
description: "从飞书(Lark)分享链接/知识库提取完整内容并转 Markdown：密码解锁、页面内部 API 拉目录树、懒加载虚拟列表滚动收集、[data-block-id] 块级 DOM 提取、Python 清洗。Use when 用户给飞书 wiki/docx 链接要提取/导入/保存全文，或需要批量抓取飞书知识库。"
version: 1.1.0
tags: [feishu, lark, wiki, docx, extraction, markdown, web-scraping]
---

# 飞书文档/知识库内容提取（Feishu Doc Extraction）

> 验证于 2026-08：从密码保护的飞书分享知识库「AI项目603」成功提取 23 篇文档目录，单篇（07Milvus快速入门）清洗为 6.2K 字符标准 Markdown。

## 触发条件

- 用户给飞书 wiki/docx 分享链接（`xxx.feishu.cn/wiki/...` 或 `/docx/...`），要求导入知识库/保存/提取内容
- 需要批量抓取飞书知识库所有文档
- 飞书文档内容是 Canvas/虚拟列表渲染，常规快照/curl 拿不到正文

## 与腾讯文档提取的区别

腾讯文档用 textPool 解码（见 `tencent-docs-extraction` 等 skill）；**飞书文档走「页面内部 API + DOM 块提取」**，路径完全不同，别混用。

## 完整流程

### Step 1 打开链接，识别访问形态

```
browser_navigate(分享链接)
```

- 出现「请输入密码访问」→ 问用户要密码 → browser_type 输入 → browser_click 确定
  - **ref 会过期**：browser_type 报 Unknown ref 时先重新 browser_snapshot 再操作
- 密码解锁后 cookie 在同一浏览器会话内**延续到所有子文档**（导航到子节点无需再解锁）
- 出现「登录/注册」→ 链接需要登录态，引导用户手动登录或换可访问链接

### Step 2 知识库首页 → 页面内部 API 拉完整目录

飞书知识库（wiki）首页加载时浏览器会调用内部 API，可在 console 里直接 fetch 复用（带解锁 cookie）：

```
https://<tenant>.feishu.cn/space/api/wiki/v2/tree/get_info/?space_id=<SPACE_ID>&with_space=true&with_perm=true&expand_shortcut=true&need_shared=true&exclude_fields=5&with_deleted=true&wiki_token=<ROOT_TOKEN>
```

- space_id 从页面网络请求里找（或 performance entries）；wiki_token 即页面 URL 里的根节点 token
- 响应 `data.tree.child_map[根token]` = 子节点 token 列表；`data.tree.nodes[token]` = 节点详情
- 关键字段：`title`、`url`（可直接导航）、`obj_token`（docx 文档 token）、`obj_type`（22=docx）
- 用 `fetch(url, {credentials:'include'})` 在 browser_console 里调用

节点清单提取示例：

```js
(async () => {
  const r = await fetch(URL, { credentials: 'include' });
  const j = await r.json();
  const root = 'W3utw...';  // 根 wiki_token
  return JSON.stringify(j.data.tree.child_map[root].map(t => ({
    title: j.data.tree.nodes[t]?.title,
    url: j.data.tree.nodes[t]?.url,
    obj_token: j.data.tree.nodes[t]?.obj_token
  })), null, 1);
})()
```

### Step 2.5 嵌套文件夹递归（知识库可能是多层树）

`get_info` 默认只返回**一层** child_map。知识库有文件夹嵌套（实测 4 层：根→优秀项目参考→金融→产品立项书→4篇AI投顾）时，必须 BFS/DFS 递归：对每个 `has_child=true` 的节点再调一次 `get_info`（wiki_token 换为该节点 token），把 `child_map[token]` 并入全树。实测全库 57 个节点。

⚠️ **`get_info` 的行为随当前页面变化**：在子文档页面调用可能返回空 child_map。先 `browser_navigate` 回知识库首页（根节点 URL），再跑递归脚本。`get_node` 只返回节点自身，不含子节点列表。

### Step 3 单篇文档 → 懒加载滚动 + 块级收集

飞书 docx 正文是**虚拟列表**，只渲染视口附近；正文 REST 接口走内部 websocket，resource entries 里找不到 → **直接 DOM 提取**：

1. 导航到节点 URL（`browser_navigate(node.url)`）
2. 找滚动容器：`document.querySelector('.bear-web-x-container')`（scrollHeight 远大于 clientHeight 的那个）
3. 边滚边收集：每次 `scroller.scrollTop += clientHeight * 0.8`，等待 ~200ms，收集当前视口所有叶子块
4. 收集对象：`document.querySelectorAll('[data-block-id]')`，**跳过容器块**（class 含 `docx-page-block|docx-view-block|docx-file-block`）
5. 按块文本 Set 去重（虚拟列表复用 DOM，滚动中同一块会重复渲染）
6. 块类型从 class 判断：`heading2-`(##) / `heading3-`(###) / `text-`(段落) / `bullet-`(列表) / `code-`(代码块) / `image-`(图片，文本为空可跳过)

⚠️ **不要用 `.render-unit-wrapper` 收集**——粒度太粗（跨块重叠），滚动快照间内容互相包含，去重困难。用 `[data-block-id]` 叶子块。

核心收集脚本（**增强版，长文档必用**：guard 150 + 动态 maxScroll + atBottom 校验。2026-08 实测 doc3：guard 60 停在 2.6 万 px 只抓到 557 块，完整文档 5.9 万 px / 1141 块）：

```js
(async () => {
  await new Promise(r => setTimeout(r, 2000));          // 等文档渲染完
  const scroller = document.querySelector('.bear-web-x-container') || document.scrollingElement;
  if (!scroller) return JSON.stringify({n: 0, reason: 'no-scroller'});
  scroller.scrollTop = 0;
  const blocks = []; const seen = new Set();
  const collect = () => {
    document.querySelectorAll('[data-block-id]').forEach(el => {
      const cls = (el.className || '').toString();
      if (/docx-page-block|docx-view-block|docx-file-block/.test(cls)) return;
      const t = (el.textContent || '').replace(/\u200b/g, '').replace(/\u200e/g, '').trim();
      if (!t || seen.has(t)) return; seen.add(t);
      let c = 't';
      if (cls.includes('heading2')) c = 'h2';
      else if (cls.includes('heading3')) c = 'h3';
      else if (cls.includes('heading4')) c = 'h4';
      else if (cls.includes('bullet')) c = 'b';
      else if (cls.includes('code')) c = 'c';
      blocks.push([c, t]);
    });
  };
  await new Promise(r => setTimeout(r, 500)); collect();
  let lastY = -1, guard = 0, maxScroll = scroller.scrollHeight;
  while (guard < 150) {
    guard++;
    scroller.scrollTop += scroller.clientHeight * 0.8;
    if (scroller.scrollTop >= maxScroll) scroller.scrollTop = maxScroll; // 钳制到当前已知高度
    await new Promise(r => setTimeout(r, 150)); collect();
    if (scroller.scrollTop === lastY) break;            // 滚不动 = 到底
    lastY = scroller.scrollTop;
    if (scroller.scrollHeight > maxScroll) maxScroll = scroller.scrollHeight; // 懒加载让高度继续增长
  }
  window.__blocks = blocks;                             // [type, text] 数组留在页面，供分段取回
  return JSON.stringify({n: blocks.length, chars: blocks.reduce((a,b)=>a+b[1].length,0), guard,
    atBottom: scroller.scrollTop + scroller.clientHeight >= scroller.scrollHeight - 30});
})()
```

- ⚠️ **`atBottom` 必须为 `true` 才算抓全**；false = 没滚到底，加大 guard 重跑。旧版「guard 80 + 强制滚底一次」对 5 万+ px 文档仍会漏（80 次仅约 3.5 万 px，且 scrollHeight 边滚边涨）
- 结果存 `window.__blocks`（[type, text] 数组），多次 browser_console 分段取回（切片大小与衔接校验见 `references/batch-two-step-recipe.md`）。**取回判据看 chars 不看块数**：实测 chars < 24000 时 1108~1336 块单次返回完整；chars > ~24000 才分段（280 块/段）
- 合并校验：`python scripts/merge_feishu_parts.py --name NAME --expect N`（块数必须等于脚本返回的 n），通过后 `rm -f NAME_part*.json`，再跑清洗脚本

### Step 4 Python 清洗 → Markdown

用 `scripts/clean_feishu_blocks.py`（见支持文件）：
- 去零宽空格 `\u200b`、压缩空白
- 代码块文本形如「代码块Markdown复制docker-compose up」→ 正则提取真实代码 + 语言映射（markdown→yaml 等）
- heading2/3 → `##`/`###`；bullet → `- `；image → 跳过
- 输出带来源注释的 Markdown 文件

## 批量抓取：并行子 agent（≥5 篇时用 delegate_task）

单篇两步法在 3 篇内自己抓；文档多（>5 篇）用并行子 agent：

- 把**收集脚本全文 + 密码 + 落盘绝对路径 + 文件名清单**全部塞进 `delegate_task` 的 context（子 agent 无会话记忆，必须自带完整说明）
- 每个子 agent 抓 5-8 篇，返回只给状态行（`文件名 | 块数 | 字符数 | 状态 ok/空/分段`），**不要把正文带进主上下文**
- 最多 3 并发（delegation.max_concurrent_children），多组分批；第二批要等第一批完成
- 子 agent 常撞工具调用上限（max_iterations）留下 part 文件/半成品 → **完成后必须扫 `raw/` 目录核对**：缺失的、被登录墙挡的用 docx 直链补抓
- 子 agent 会**擅改共享脚本**（实测给 build_markdown.py 加了 `SKIP = {'<名>'}` 导致后续重新生成被静默跳过）→ 批量结束后 `grep -n "SKIP" build_markdown.py` 检查，把 SKIP 清空

## 坑（Pitfalls）

1. browser_console 的 ref 过期：交互前重新 snapshot
2. 虚拟列表不滚动 = 拿不全：必须滚到底。⚠️ **「guard 上限」和「scrollTop 不再变化」两个停止条件都不可靠**——scrollHeight 边滚边增长（懒加载），且单次滚距 = 0.8×clientHeight，guard 60-80 只够 2.6~3.5 万 px。实测 doc3 guard 60 停在 2.6 万 px 只抓到 557 块，完整文档 5.9 万 px / 1141 块（静默漏掉整个尾部，返回的 JSON 依然合法完整，不会报错）。用增强版脚本（guard 150 + 动态 maxScroll + atBottom 校验），**以返回的 `atBottom === true` 为抓全标准**；false 就加大 guard 重跑。另可抽查 `window.__blocks.slice(-3)` 确认收尾是合理结尾（附录/结语），不是文中间
3. 重复数据：滚动快照重叠 → 用叶子块 + Set 去重，不要用大容器块
4. 图片内容 textContent 为空 → Markdown 里留占位或提示用户
5. 代码块语言标签是正文块（「代码语言：python」是 text 块，不是 code 块属性）
6. 清洗脚本路径坑：脚本和 JSON 放同目录，用相对文件名（Windows 下子目录相对路径易踩 FileNotFoundError）
7. 正文很长时滚动收集返回可能超限：先收集到 `window.__blocks`，再分批取回，不要一次性返回。**批量抓取时一律用两步法**。判据以 chars 为主：**实测（2026-08-10 七篇批量）chars < 24000 时单次返回 1108~1336 块均完整，未见截断**；chars > ~24000（如 25617/25820）才必须分段，分段 280 块/段（每段约 13~18K 字符）安全。**注意：单遍滚动收集的 n 可能因没滚到底而偏小（2026-08 实测首次 722 块，强制滚底后 901 块）**，用增强版脚本以 atBottom 为准，n 不齐不代表落盘错。个别环境/超长单块仍可能提前截断，取回后校验：切片首尾衔接 + 总块数 == `window.__blocks.length`
8. 两步法脚本易犯变量错：collect() 里 push 到 `window.__blocks`（不是局部 `blocks`），否则报 `ReferenceError: blocks is not defined`
9. 空文档形态：正文只有文件附件（class 含 `docx-file-block`/`docx-view-block`，如「分享的文件」页）或只有页面容器块时，收集结果 n=0 —— 属正常，保存 `[]` 并在摘要标记「空文档」，不要误判为脚本失败
10. 分段 JSON 落盘后重读校验：`json.load` 每段通过且块数与浏览器端一致即可；文件字符数与浏览器返回的 chars 允许有几十字符的转义表示差异，内容完整即合格
11. 同一文档两次收集块数会不同：虚拟列表渲染时机差异（实测同一篇 499 vs 495 块）。这是正常波动，以 `window.__blocks` 那次为准，不要因为数字对不上就重抓或怀疑落盘出错；只要合并后与本次 n 基本一致（±5）即合格
12. 代码块 textContent 丢失换行：飞书代码块逐行渲染，`el.textContent` 会把各行直接拼接（实测 `codeHasNewline: false`，如 `import jsonimport osimport re` 无 `\n`）。代码保真重要时需对 code 块按行级子元素单独收集再 join('\n')；否则接受粘连并在清洗阶段说明（教学文档里代码是关键内容，转 Markdown 前先确认是否需要保真）
13. 多 agent/多会话并发写同一 raw 目录时，`merge_feishu_parts.py --expect N` 的序号扫描会把其他 agent 的同名 part 文件一起算进去（2026-08 实测：误收 sibling 的 `ARCHITECTURE_part4.json`，合并 996 块 vs 浏览器 632 块，MISMATCH 报错）。`--expect` 报 MISMATCH 时**先查 `ls <名>_part*.json` 有没有别人的/陈旧的 part**，删掉或改名后再合并，不要直接重抓文档；从源头规避：自己的 part 文件用唯一后缀（`<名>_sa_partN.json`）再手动合并，清理时只删自己的
14. 不要尝试「本地 HTTP 服务器接收浏览器 POST 直传数据」的捷径：浏览器可能运行在远程/隔离环境（即使 stealth 特征显示 local），fetch 127.0.0.1 直接 Failed to fetch（2026-08 实测，白起一个 Python HTTP server + 探测浪费多轮）。标准两步法（window.__blocks + 分段取回 + write_file/merge 脚本）才是可靠路径；真想试先 fetch 探测连通性，不通立即放弃
15. Windows 下用 heredoc 写 `/tmp/x.py` 再 `python /tmp/x.py` 会失败：Windows 原生 python 把 `/tmp` 解析为 `C:\tmp`（git-bash 的 /tmp 是另一个位置）。辅助脚本一律用 write_file 写到 Windows 绝对路径（如 `C:/Users/<user>/AppData/Local/Temp/x.py`）再运行

13. **分享链接被登录墙拦截（不是密码框）**：同一分享者名下部分 wiki 链接匿名可开、部分导航直接 302 到 `accounts.feishu.cn/accounts/page/login?app_id=2&...&redirect_uri=...` —— 这是硬登录墙，不是「请输入密码访问」框；登录页只有扫码登录，无访客/密码入口。`browser_navigate` 超时后**先 `browser_console` 查 `location.href`** 确认是否跳登录，别盲目重试同一 URL（3 次即触发循环警告）。**⚠️ 先试 docx 直链绕过再放弃**：把同一 token 换成 docx 路径 `https://<tenant>.feishu.cn/docx/<token>` 导航——如果该 token 实际是 docx 的 obj_token（分享者给的就是文档 token 而非 wiki 节点 token），会 302 到真实 wiki 地址并正常加载正文（2026-08 实测：`wiki/Cl9Kd8TISo0CLrxQpkHcJ3M6nch` 撞登录墙 → `docx/Cl9Kd8TISo0CLrxQpkHcJ3M6nch` 成功，302 到 `wiki/A0OBwCBCfihQ6AkarSFciN4znLd`；且该 token 用 `space/api/wiki/v2/tree/get_node/` 查会返回 `code: 920004002 SourceNotExist`——这正说明它是非本 space 的 obj_token，不代表文档不可达）。绕过失败（token 是纯 wiki 节点 token）才需真实登录态，及时上报父代理/用户，不要无限重试；密码解锁 cookie（如 Wolin0603）只对密码墙文档有效，救不了登录墙

14. **browser_console 多行脚本报 `SyntaxError: Unexpected end of input`**：browser_console 对带换行的多行 IIFE 解析不稳定；遇到该报错把整个表达式压缩成单行（分号连接、不用 `?.` 可选链改显式判断）再执行。收集/取回脚本建议直接以单行形式粘贴执行
15. **两次不完整收集可以并集合并，别只认 atBottom**：个别超长文档（scrollHeight 4.8 万 px 级）即使多遍重跑，单遍仍可能只收到 1225 块 vs 期望 1539（但该遍有头有尾、含「最终结论」，说明覆盖全文只是中间表格块渲染波动漏掉）。此时保留两批收集：先收集（覆盖开头到中间）+ 后收集（可能覆盖到结尾），Python 按 `(cls,text)` 去重做并集（先收集在前、后收集中新块按序追加），**内容优先于顺序**；表格类 text 块重复率高，去重效果好。合并后块数 > 任一单遍即说明补回了缺口。若已知 part 文件已含 1-x 章、新收集含完整结尾（含「最终结论」等收尾标志），用「旧 part 全量 + 新收集新块追加」即可
16. **part 合并别覆盖已含早期 part 的主文件**：把 part1-2 合并进主文件后，再用 `glob('*_part*.json')` 合并其余 part 会**覆盖主文件**（只剩 part3-8，part1-2 丢失）。教训：合并前先备份主文件，或先读主文件已有 blocks 再 append 其余 part 后整体写回；真丢了可从已生成的 `markdown/` 中间产物恢复开头文本（build 脚本曾输出 200 块版 md，其结尾与后续 part 开头无缝衔接时可直接拼接 md，再在清洗脚本 SKIP 集合跳过该文件防覆盖）
17. **子 agent 改共享脚本的 SKIP 陷阱**：并行子 agent 批量抓取时，可能给清洗脚本加 `SKIP = {'<文档名>'}`「防止覆盖手动拼接产物」，结果后续重新生成时该文档被静默跳过、md 不更新。批量结束后 `grep -n "SKIP" build_markdown.py` 检查并清空；同理验证 `raw/` 下没有残留 `_part*.json`（子 agent 合并失败会留半成品）。

## 导入飞书（Plan B：无需 convert 权限，2026-08 实测 40 篇）

抓取只是「读」侧。导入自己的飞书云空间/知识库**不依赖 lark-mcp**（`references/lark-openapi-mcp.md` 里的 MCP 方案可选但非必需）。直接用 REST API + tenant_access_token 即可。

### 权限矩阵（实测，2026-08）
| 操作 | 所需 scope | 实测 |
|---|---|---|
| 建文档 / 写块 | `docx:document` | ✅ 常见已有 |
| 列知识空间 | `wiki:wiki:readonly` | ✅ |
| 知识空间写入/移动 | `wiki:wiki` | 用户到开放平台补 |
| Markdown→块（convert） | `docx:document.block:convert` | ❌ **常缺 → 用 Plan B** |
| 通讯录查 open_id | `contact:...` | ❌ 常缺 |
| 租户域名 | `tenant:tenant:readonly` | ❌ 常缺 |

- token：`POST /open-apis/auth/v3/tenant_access_token/internal`，body `{app_id, app_secret}`（.env `FEISHU_APP_ID/SECRET`）
- 权限错误 `99991672`：错误信息自带开放平台申请链接，直接转给用户点

### Plan B 导入流程（不用 convert）
1. raw `[cls,text]` → docx Block：
   - heading2 → `block_type 4` + `{"heading2": {"elements": [...]}}`；heading3→5、heading4→6；bullet→12；code→14（内容先正则 `代码块\s*(.*?)复制\s*(.*)$` 去「代码块XXX复制」UI 噪音）；text→2
   - 内联 `**bold**` / `` `code` `` 拆成多个 `text_run`（`text_element_style: {bold:true}` / `{inline_code:true}`）
2. `POST /open-apis/docx/v1/documents` `{title}` → `document_id`
3. `GET /open-apis/docx/v1/documents/{id}/blocks?page_size=500` → 根块（`block_type 1` page）
4. `POST /open-apis/docx/v1/documents/{id}/blocks/{root}/children` `{children:[...]}` 分批（40 块/批 + 0.2s 间隔，长文档每篇 5-10 秒）

### 应用云空间可见性（大坑）
- 应用身份创建的文档落在**应用云空间**（`GET /open-apis/drive/v1/files` 可见），**用户个人空间看不到**
- 修复：`PATCH /open-apis/drive/v1/permissions/{token}/public?type=docx` body `{"link_share_entity":"tenant_editable","link_perm":"edit"}` → 组织内可编辑，用户搜索标题即可见/编辑
- 文档链接域名 = 应用租户域名。**不要放弃**：`POST /open-apis/drive/v1/metas/batch_query` body `{"request_docs":[{"doc_token":"<docx_token>","doc_type":"docx"}],"with_url":true}` 返回 `data.metas[].url`（实测拿到 `https://fcn501hdf8xr.feishu.cn/docx/...`）→ 域名 + 各文档 token 拼成全部可点击链接，生成 `文档链接清单.md` 给用户
- 移入知识空间：应用必须是目标空间**成员**（即使有 wiki:wiki，`wiki/v2/spaces` 仍为空）→ 让用户在空间设置→成员管理里添加应用机器人；然后 `wiki.v2.spaceNode.moveDocsToWiki`
- **space_id 是数字**：用户给的知识空间链接 `xxx.feishu.cn/wiki/<token>` 里的 token 是 **wiki_token（首页节点）** 不是 space_id → 用 `GET /open-apis/wiki/v2/spaces/get_node?token=<wiki_token>&obj_type=wiki` 反查 `data.node.space_id`（数字）
- **move_docs_to_wiki 一次一篇**：body `{"parent_wiki_token":"<首页wiki_token>","obj_type":"docx","obj_token":"<docx_token>"}` —— 字段是 `obj_token` 单数；写 `obj_tokens` 数组会报 `99992402 obj_token is required`
- ⚠️ **应用几乎无法加入知识空间成员（2026-08 实测死路）**：「添加管理员」弹窗搜索只支持「用户、群组、部门或用户组」，**没有应用/机器人入口**；`spaceMember.create` 添加应用自己需要已有空间权限（鸡生蛋，报 `131006 permission denied: wiki space permission denied`）。API 移动（move_docs_to_wiki）报 `131006 no destination parent node permission` 即此原因 → **兜底方案：文档设 tenant_editable 后让用户手动移动**（打开链接 → 右上角「···」→「移动到」→ 选知识空间），提供 `文档链接清单.md` 批量操作指引

### API 路径速查（实测）
| 操作 | 路径 |
|---|---|
| 建文档 | `POST /open-apis/docx/v1/documents` |
| 列表块 | `GET /open-apis/docx/v1/documents/{id}/blocks` |
| 写子块 | `POST /open-apis/docx/v1/documents/{id}/blocks/{root}/children` |
| Markdown转块 | `POST /open-apis/docx/v1/documents/blocks/convert`（**不是** `/{id}/convert`，404） |
| 设公开权限 | `PATCH /open-apis/drive/v1/permissions/{token}/public?type=docx` |
| 删文档 | `DELETE /open-apis/drive/v1/files/{token}?type=docx` |
| 列空间文件 | `GET /open-apis/drive/v1/files?page_size=100` |
| 列知识空间 | `GET /open-apis/wiki/v2/spaces` |

⚠️ 公开/删除接口缺 `?type=docx` 参数 → `99992402 field validation failed`。完整脚本模板见 `templates/import_feishu.py`；API/权限/错误码全表见 `references/feishu-import-api.md`。

**查真实 API 路径的可靠方法**：别猜路径（实测 `/documents/convert`、`/documents/{id}/convert` 都 404）。`pip install lark-oapi` 后直接 grep SDK 源码：`grep -rn "uri = " <site-packages>/lark_oapi/api/docx/v1/model/*.py`，每个 request 模型里都有 `self.xxx.uri = "/open-apis/..."` + `http_method` + `token_types`（TENANT/USER）—— 比翻文档快得多。字段名同样以 SDK 的 request_body 模型为准（如 convert 是 `content_type` 不是 `type`）。

### 批量导入要点
- 前台 600s 会超时（42 篇约 8 分钟）→ 用 `terminal(background=true, notify_on_complete=true)`
- 重复检测：导入后列应用空间，`Counter(name)` 找重名文档（实测 Redis 出现 2 次）→ `DELETE ...?type=docx` 清理

## 支持文件

- `scripts/collect_blocks.js` — 浏览器 console 标准收集脚本（guard 150 + atBottom 校验）
- `scripts/clean_feishu_blocks.py` — raw JSON → Markdown 清洗
- `scripts/merge_feishu_parts.py` — 分段 JSON 合并 + 块数校验
- `references/batch-two-step-recipe.md` — 大文档两步法取回细节
- `references/lark-openapi-mcp.md` — 官方 MCP 方案（可选）
- `references/feishu-import-api.md` — **导入 API 路径 / 权限 scope / 错误码全表**
- `templates/import_feishu.py` — **Plan B 导入脚本模板（无 convert 权限版）**

## 相关

- 腾讯文档提取（textPool 解码，不同平台）：`tencent-docs-extraction` / `restricted-doc-extraction` / `canvas-doc-extraction`
- 群聊多 agent 场景：MCP 是 per-profile 配置，给哪个 agent 用 lark-mcp 就在它的 `profiles/<name>/config.yaml` 里配
